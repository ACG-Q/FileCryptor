package main

import (
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"strings"

	crypto "github.com/ACG-Q/FileCryptor/utils"
)

const (
	defaultKeyFile       = "_key.bin"
	defaultEncExt        = "_encrypted.bin"
	defaultDecryptPrefix = "_decrypted"
)

func main() {
	if len(os.Args) > 1 && (os.Args[1] == "-h" || os.Args[1] == "--help") {
		printHelp()
		return
	}

	if len(os.Args) < 2 {
		printHelp()
		return
	}

	switch os.Args[1] {
	case "encrypt":
		handleEncryptCmd()
	case "decrypt":
		handleDecryptCmd()
	case "help":
		handleHelpCmd()
	default:
		fmt.Printf("未知命令: %q\n\n", os.Args[1])
		printHelp()
	}
}

func handleEncryptCmd() {
	cmd := flag.NewFlagSet("encrypt", flag.ExitOnError)
	cmd.Usage = encryptCmdHelp

	password := cmd.String("p", "", "")
	outputFile := cmd.String("o", "", "")
	keyFile := cmd.String("k", "", "")
	force := cmd.Bool("f", false, "")
	cmd.Parse(os.Args[2:])

	if cmd.NArg() == 0 || *password == "" {
		cmd.Usage()
		os.Exit(1)
	}

	inputFile := cmd.Arg(0)
	handleEncrypt(inputFile, *password, *outputFile, *keyFile, *force)
}

func handleDecryptCmd() {
	cmd := flag.NewFlagSet("decrypt", flag.ExitOnError)
	cmd.Usage = decryptCmdHelp

	password := cmd.String("p", "", "")
	outputFile := cmd.String("o", "", "")
	keyFile := cmd.String("k", "", "")
	force := cmd.Bool("f", false, "")
	cmd.Parse(os.Args[2:])

	if cmd.NArg() == 0 || *password == "" {
		cmd.Usage()
		os.Exit(1)
	}

	inputFile := cmd.Arg(0)
	handleDecrypt(inputFile, *password, *keyFile, *outputFile, *force)
}

func handleEncrypt(inputPath, password, outputPath, keyPath string, force bool) {
	if !fileExists(inputPath) {
		exitWithError("输入文件不存在")
	}

	if outputPath == "" {
		outputPath = genOutputPath(inputPath, defaultEncExt)
	}
	if keyPath == "" {
		keyPath = genOutputPath(outputPath, defaultKeyFile)
	}

	ensureFileNotExists(outputPath, force)
	ensureFileNotExists(keyPath, force)

	data, err := readFile(inputPath)
	if err != nil {
		exitWithError("读取文件失败: " + err.Error())
	}

	result, err := crypto.Encrypt(data, password)
	if err != nil {
		exitWithError("加密失败: " + err.Error())
	}

	writeFile(keyPath, result.KeyFile, force)
	writeFile(outputPath, result.EncryptedData, force)

	fmt.Printf("加密成功\n输出文件: %s\n密钥文件: %s\n", outputPath, keyPath)
}

func handleDecrypt(inputPath, password, keyPath, outputPath string, force bool) {
	if !fileExists(inputPath) {
		exitWithError("输入文件不存在")
	}

	if keyPath == "" {
		keyPath = genKeyPath(inputPath)
		if !fileExists(keyPath) {
			exitWithError("未找到密钥文件，请手动指定")
		}
	}

	if outputPath == "" {
		outputPath = genOutputPath(inputPath, defaultDecryptPrefix)
	}

	ensureFileNotExists(outputPath, force)

	encryptedData, err := readFile(inputPath)
	if err != nil {
		exitWithError("读取文件失败: " + err.Error())
	}

	keyData, err := readFile(keyPath)
	if err != nil {
		exitWithError("读取密钥文件失败: " + err.Error())
	}

	decryptedData, err := crypto.Decrypt(encryptedData, keyData, password)
	if err != nil {
		exitWithError("解密失败: " + err.Error())
	}

	writeFile(outputPath, decryptedData, force)

	fmt.Printf("解密成功\n输出文件: %s\n", outputPath)
}

func genOutputPath(inputPath, suffix string) string {
	return strings.TrimSuffix(inputPath, filepath.Ext(inputPath)) + suffix
}

func genKeyPath(inputPath string) string {
	return genOutputPath(inputPath, defaultKeyFile)
}

func readFile(path string) ([]byte, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("读取文件 %s 失败: %w", path, err)
	}
	return data, nil
}

func writeFile(path string, data []byte, force bool) {
	if !force && fileExists(path) {
		exitWithError(fmt.Sprintf("文件 %s 已存在, 请使用 -f 强制覆盖", path))
	}

	err := os.WriteFile(path, data, 0600)
	if err != nil {
		exitWithError(fmt.Sprintf("写入文件 %s 失败: %v", path, err))
	}
}

func ensureFileNotExists(path string, force bool) {
	if !force && fileExists(path) {
		exitWithError(fmt.Sprintf("文件 %s 已存在, 请使用 -f 强制覆盖", path))
	}
}

func fileExists(path string) bool {
	_, err := os.Stat(path)
	return !os.IsNotExist(err)
}

func exitWithError(msg string) {
	fmt.Fprintln(os.Stderr, "错误:", msg)
	os.Exit(1)
}

func printHelp() {
	fmt.Println(`文件加密解密工具 v1.2

命令结构:
  filecrypt [全局选项] <命令> [命令选项] 输入文件

可用命令:
  encrypt     加密文件
  decrypt     解密文件
  help        显示帮助信息

全局选项:
  -h, --help  显示帮助信息

示例:
  加密: filecrypt encrypt -p mypass document.pdf
  解密: filecrypt decrypt -p mypass document_encrypted.bin`)
}

func encryptCmdHelp() {
	fmt.Println(`加密命令选项:
  -p string   加密密码（必须）
  -o string   输出文件路径（默认：输入文件_encrypted.bin）
  -k string   密钥保存路径（默认：输入文件_key.bin）
  -f         强制覆盖已存在文件`)
}

func decryptCmdHelp() {
	fmt.Println(`解密命令选项:
  -p string   解密密码（必须）
  -o string   输出文件路径（默认：加密文件名_decrypted）
  -k string   密钥文件路径（默认自动推导）
  -f         强制覆盖已存在文件`)
}

func handleHelpCmd() {
	if len(os.Args) < 3 {
		printHelp()
		return
	}

	switch os.Args[2] {
	case "encrypt":
		encryptCmdHelp()
	case "decrypt":
		decryptCmdHelp()
	default:
		printHelp()
	}
}
