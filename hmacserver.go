// Responds to challenges by returning the HMAC of the challenge, proving that you have the secret.
// Example usage: curl -v "127.0.0.1:12345/chall?chall=A12345CA21D6CDD57CD2B747FCA14708"
// Modify isValidChallenge as per your requirements.
package main

import (
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"log"
	"net/http"
)

// Configuration
var (
	// Make sure you change these:
	secret = "12345"
	port   = "12345"
)

func isValidChallenge(s string) bool {
	if len(s) != 32 {
		fmt.Println("Error: Challenge is length " + fmt.Sprint(len(s)) + " expected length 32")
		return false
	}
	for _, r := range s {
		if (r < 'A' || r > 'Z') && (r < '0' || r > '9') {
			return false
		}
	}
	return true
}

//Credits: https://golangcode.com/generate-sha256-hmac/
func genHMAC(s string) string {
	data := s
	fmt.Printf("Secret: %s Data: %s\n", secret, data)

	// Create a new HMAC by defining the hash type and the key (as byte array)
	h := hmac.New(sha256.New, []byte(secret))

	// Write Data to it
	h.Write([]byte(data))

	// Get result and encode as hexadecimal string
	bytes := h.Sum(nil)
	result := hex.EncodeToString(bytes)
	return result
}

func handleChallenge(w http.ResponseWriter, r *http.Request) {
	var challenge = r.URL.Query().Get("chall")
	if !isValidChallenge(challenge) {
		w.WriteHeader(400)
		return
	}
	var body string
	body = genHMAC(challenge)
	fmt.Println("body:", body)
	w.Write([]byte(body))
}

func main() {
	handler := http.HandlerFunc(handleChallenge)
	http.Handle("/chall", handler)
	log.Fatal(http.ListenAndServe(":"+port, nil))
}
