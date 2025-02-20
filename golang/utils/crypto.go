package crypto

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"crypto/sha256"
	"errors"
	"io"

	"golang.org/x/crypto/pbkdf2"
)

const (
	SaltSize   = 16
	NonceSize  = 12
	TagSize    = 16
	KeySize    = 32
	Iterations = 100000
)

type EncryptResult struct {
	EncryptedData []byte // 加密后的文件数据
	KeyFile       []byte // 密钥文件
}

// 加密函数
func Encrypt(data []byte, password string) (*EncryptResult, error) {
	// 1. 生成盐值
	salt := make([]byte, SaltSize)
	if _, err := io.ReadFull(rand.Reader, salt); err != nil {
		return nil, err
	}

	// 2. 从密码派生K1密钥
	k1 := pbkdf2.Key([]byte(password), salt, Iterations, KeySize, sha256.New)

	// 3. 生成随机K2密钥
	k2 := make([]byte, KeySize)
	if _, err := io.ReadFull(rand.Reader, k2); err != nil {
		return nil, err
	}

	// 4. 使用K1加密K2
	k2Nonce := make([]byte, NonceSize)
	if _, err := io.ReadFull(rand.Reader, k2Nonce); err != nil {
		return nil, err
	}

	k1Block, err := aes.NewCipher(k1)
	if err != nil {
		return nil, err
	}

	k1Gcm, err := cipher.NewGCM(k1Block)
	if err != nil {
		return nil, err
	}

	encryptedK2 := k1Gcm.Seal(nil, k2Nonce, k2, nil)
	k2Tag := encryptedK2[len(encryptedK2)-TagSize:]
	encryptedK2 = encryptedK2[:len(encryptedK2)-TagSize]

	// 5. 使用K2加密数据
	dataNonce := make([]byte, NonceSize)
	if _, err := io.ReadFull(rand.Reader, dataNonce); err != nil {
		return nil, err
	}

	k2Block, err := aes.NewCipher(k2)
	if err != nil {
		return nil, err
	}

	k2Gcm, err := cipher.NewGCM(k2Block)
	if err != nil {
		return nil, err
	}

	encryptedData := k2Gcm.Seal(nil, dataNonce, data, nil)
	dataTag := encryptedData[len(encryptedData)-TagSize:]
	encryptedData = encryptedData[:len(encryptedData)-TagSize]

	// 6. 打包密钥文件
	keyFile := make([]byte, 0, SaltSize+NonceSize+TagSize+len(encryptedK2))
	keyFile = append(keyFile, salt...)
	keyFile = append(keyFile, k2Nonce...)
	keyFile = append(keyFile, k2Tag...)
	keyFile = append(keyFile, encryptedK2...)

	// 7. 打包加密文件
	finalData := make([]byte, 0, NonceSize+TagSize+len(encryptedData))
	finalData = append(finalData, dataNonce...)
	finalData = append(finalData, dataTag...)
	finalData = append(finalData, encryptedData...)

	return &EncryptResult{
		EncryptedData: finalData,
		KeyFile:       keyFile,
	}, nil
}

// 解密函数
func Decrypt(encryptedData []byte, keyFile []byte, password string) ([]byte, error) {
	if len(keyFile) < SaltSize+NonceSize+TagSize+KeySize {
		return nil, errors.New("invalid key file size")
	}

	// 1. 解析密钥文件
	salt := keyFile[:SaltSize]
	k2Nonce := keyFile[SaltSize : SaltSize+NonceSize]
	k2Tag := keyFile[SaltSize+NonceSize : SaltSize+NonceSize+TagSize]
	encryptedK2 := keyFile[SaltSize+NonceSize+TagSize:]

	// 2. 派生K1密钥
	k1 := pbkdf2.Key([]byte(password), salt, Iterations, KeySize, sha256.New)

	// 3. 使用K1解密K2
	k1Block, err := aes.NewCipher(k1)
	if err != nil {
		return nil, err
	}

	k1Gcm, err := cipher.NewGCM(k1Block)
	if err != nil {
		return nil, err
	}

	encryptedK2WithTag := make([]byte, len(encryptedK2)+TagSize)
	copy(encryptedK2WithTag, encryptedK2)
	copy(encryptedK2WithTag[len(encryptedK2):], k2Tag)

	k2, err := k1Gcm.Open(nil, k2Nonce, encryptedK2WithTag, nil)
	if err != nil {
		return nil, err
	}

	// 4. 解析加密文件
	dataNonce := encryptedData[:NonceSize]
	dataTag := encryptedData[NonceSize : NonceSize+TagSize]
	encryptedContent := encryptedData[NonceSize+TagSize:]

	// 5. 使用K2解密数据
	k2Block, err := aes.NewCipher(k2)
	if err != nil {
		return nil, err
	}

	k2Gcm, err := cipher.NewGCM(k2Block)
	if err != nil {
		return nil, err
	}

	encryptedContentWithTag := make([]byte, len(encryptedContent)+TagSize)
	copy(encryptedContentWithTag, encryptedContent)
	copy(encryptedContentWithTag[len(encryptedContent):], dataTag)

	decryptedData, err := k2Gcm.Open(nil, dataNonce, encryptedContentWithTag, nil)
	if err != nil {
		return nil, err
	}

	return decryptedData, nil
}
