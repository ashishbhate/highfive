package main

import (
	"fmt"
	"log"
	"net/http"
	"os/exec"
)

var names = make(chan string, 10)

func doHighFive() {
	for name := range names {
		cmd := exec.Command("python3", "/home/dietpi/Code/highfive/hw/hw.py", name)
		if err := cmd.Run(); err != nil {
			fmt.Println(err)
		}
	}
}

func highFive(w http.ResponseWriter, r *http.Request) {
	switch r.Method {

	case "GET":
		names <- "Someone"
		fmt.Fprintf(w, "Anonymous high five sent!")
		return

	case "POST":
		if err := r.ParseForm(); err != nil {
			fmt.Fprintf(w, "ParseForm() err: %v", err)
			return
		}
		name := r.FormValue("name")
		if name == "" {
			name = "Someone"
		}
		names <- name
		return

	default:
		fmt.Fprintf(w, "Only GET and POST methods are supported.")
	}
}

func main() {
	go doHighFive()
	http.HandleFunc("/", highFive)

	if err := http.ListenAndServe(":5555", nil); err != nil {
		log.Fatal(err)
	}
}
