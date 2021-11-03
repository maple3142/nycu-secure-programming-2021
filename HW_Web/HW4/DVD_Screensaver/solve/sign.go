package main

import (
	"fmt"
	"github.com/gorilla/securecookie"
	"os"
)

// var (
// 	hashKey = []byte("d2908c1de1cd896d90f09df7df67e1d4")
// 	key     = securecookie.New(hashKey, nil)
// )

func main() {
	secret_key := os.Args[1]
	key := securecookie.New([]byte(secret_key), nil)
	mp := make(map[interface{}]interface{})
	mp["username"] = os.Args[2]
	newcookie, _ := key.Encode("session", mp)
	fmt.Println(newcookie)
}
