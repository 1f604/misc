// Simple file server using HTTP basic authentication
// Allows 3 consecutive failed logins (configurable), after which all requests will be denied and server must be restarted.
// Make sure you change the configuration as specified below.
// Place files in the subdirectory in the same directory where this file is.
/* Default directory structure:
   - httpserver.go (this file)
   - filestobeserved (directory)
   - file1.html (file)
      - assets (directory)
         - file2.jpg (file)
*/
package main

import (
	"crypto/subtle"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"path"
	"strings"
	"sync"
)

// Configuration
var (
	// Make sure you change these:
	username          = "admin"
	password          = "12345"
	allowedsubdir     = "filestobeserved"
	allowedsubsubdirs = [...]string{"/", "/assets", "/random"}
	port              = "12345"
	// You can leave these as they are.
	max_failed_logins   = 3
	print_failed_logins = true
	realm               = "12345"
	default_filename    = "index.html"
)

type counter struct {
	mu sync.Mutex
	n  int
}

func (c *counter) inc() {
	c.mu.Lock()
	c.n++
	c.mu.Unlock()
}

func (c *counter) get() int {
	c.mu.Lock()
	var n = c.n
	c.mu.Unlock()
	return n
}

func (c *counter) reset() {
	c.mu.Lock()
	c.n = 0
	c.mu.Unlock()
}

var allowedDirectories = map[string]bool{}
var failed_logins = counter{n: 0}

func main() {
	for _, element := range allowedsubsubdirs {
		allowedDirectories[element] = true
	}

	handler := http.HandlerFunc(handleRequest)
	http.Handle("/", handler)
	log.Fatal(http.ListenAndServe(":"+port, nil))
}

// Have to do this because regular expressions in Go are insanely slow.
func isValidFilename(s string) bool {
	for _, r := range s {
		if (r < 'a' || r > 'z') && (r < '0' || r > '9') && r != '.' && r != '_' {
			return false
		}
	}
	return true
}

func handleAuthorized(w http.ResponseWriter, r *http.Request) {
	fmt.Println("Successful login attempt.")
	failed_logins.reset()
	filename := default_filename
	var body []byte
	var err error
	requested := path.Base(r.URL.Path)
	predir := path.Dir(r.URL.Path)
	if _, ok := allowedDirectories[predir]; !ok {
		body = []byte("Error: invalid directory:" + predir + ".")
		fmt.Println("Invalid directory requested:" + predir)
	} else {
		if isValidFilename(requested) {
			filename = requested
		}
		//fmt.Println(filename, predir)

		if !strings.HasSuffix(predir, "/") {
			predir += "/"
		}
		filepath := allowedsubdir + predir + filename
		body, err = ioutil.ReadFile(filepath)
		if err != nil {
			fmt.Println("File not found: " + filepath)
			body = []byte("Error: " + filepath + " not found.")
		} else {
			fmt.Println("File served: " + filepath)
		}
	}
	w.Write(body)
}

func handleRequest(w http.ResponseWriter, r *http.Request) {
	if failed_logins.get() >= max_failed_logins {
		w.WriteHeader(400)
		return
	}

	user, pass, ok := r.BasicAuth()

	if !ok || subtle.ConstantTimeCompare([]byte(user), []byte(username)) != 1 || subtle.ConstantTimeCompare([]byte(pass), []byte(password)) != 1 {
		failed_logins.inc()
		if print_failed_logins {
			fmt.Println(`Failed login attempt used username: "` + user + `" and password: "` + pass + `"`)
		}
		if failed_logins.get() == max_failed_logins {
			fmt.Println("Max failed login attempts reached. Please restart server.")
		}
		w.Header().Set("WWW-Authenticate", `Basic realm=`+realm)
		w.WriteHeader(401)
		return
	}

	handleAuthorized(w, r)
	return
}
