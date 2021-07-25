package main

import (
	"os"
	"time"
)

var g_filecount = 0

func iterate(path string) []string {
	var dirlist []string
	println(path)
	entries, err := os.ReadDir(path)
	if err != nil {
		panic(err)
	}
	for _, entry := range entries {
		if entry.IsDir() {
			dirlist = append(dirlist, path+"/"+entry.Name())
		} else {
			g_filecount++
		}
	}
	return dirlist
}

func countfiles(dir string) {
	dirlist := []string{dir}
	var directory string
	for {
		if len(dirlist) == 0 {
			break
		}
		directory, dirlist = dirlist[len(dirlist)-1], dirlist[:len(dirlist)-1]
		newdirs := iterate(directory)
		dirlist = append(dirlist, newdirs...)
	}
}

func main() {
	start := time.Now()
	countfiles("/tmp/data2")
	println(g_filecount)
	duration := time.Since(start)
	println(duration)
}
