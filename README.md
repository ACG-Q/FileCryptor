# FileCryptor

## 🎯 简介

**FileCryptor** 是一款跨平台、多语言的文件加密与解密工具~~，致力于为用户提供简洁高效的文件加密方案~~，全方位守护您的敏感数据安全。

**核心目标**：通过统一的密码体系，实现对所有文件的一致性加密操作，确保数据安全的同时，极大简化加密流程。

## 🤝 功能概览

- **🔒 文件加密**：支持对各种类型的文件进行加密。
- **🔓 文件解密**：支持对加密后的文件进行解密。
- **🌐 跨平台支持**：支持 Windows、macOS 和 Linux 平台。
- **📝 多语言实现**：提供 Python、Go 和 Web 版本的实现。

## 💫 加密原理

**FileCryptor** 采用双层密钥架构（K1/K2）进行文件加密，结合 PBKDF2 密钥派生算法和 AES-GCM 加密算法。

## 🎨 截图预览

### WEB端

> [!NOTE]
> 头一次，写出这么好的前端UI，就不开源了

#### 📱 首页界面

![首页](https://github.com/user-attachments/assets/69b4e088-7cd6-4aa5-8631-04e3f6ac727e)

#### 🔒 加密界面

![加密](https://github.com/user-attachments/assets/6e9dbc72-c2f5-4c5d-8ca1-d201fd6ad275)

#### 🔓 解密界面

![解密](https://github.com/user-attachments/assets/61ab57e4-b5b9-47e9-b639-7302cb75b7c1)

#### 🤝 更换密码界面

![更换密码](https://github.com/user-attachments/assets/c148e81a-f31e-4b2e-8784-67eabd1da376)

### Python

> [!NOTE]
> 好像win10和win11显示效果不一致呀，win11显示字体好小，win10显示字体好大哦

#### 🎨 Windows 10 截图

> todo: 调整完ui，再重新贴图

![加密](https://github.com/user-attachments/assets/d1bb11e6-2b2e-428b-8ed3-e1f184f58c0a)

![解密](https://github.com/user-attachments/assets/0944deaf-3164-40b6-a67f-3ac3674ea830)

#### 🎨 Windows 11 截图

### Golang

> todo: 程序存在小瑕疵，后续修改

![image](https://github.com/user-attachments/assets/74d2e5eb-ab37-4759-bd9b-679f1c96a905)

#### 📝 示例命令

- **查看帮助**

```shell
filecrypt -h
filecrypt encrypt -h
filecrypt decrypt -h
```

- **加密命令**

```shell
filecrypt encrypt -p <password> <file>
filecrypt encrypt -p <password> -o <enc_file> <file>
filecrypt encrypt -p <password> -o <enc_file> -k <enc_key> <file>
```

**默认**
enc_file: <file>_encrypted.bin
enc_key: <file>_key.bin

- **解密命令**

> 省略参数的前提是
> enc_key 和 enc_file 放在同一目录下，并且采用默认名称

```shell
filecrypt decrypt -p <password> <enc_file>
filecrypt decrypt -p <password> -o <file> <enc_file>
filecrypt decrypt -p <password> -o <file> -k <enc_key> <enc_file>
```

**注意**：

- **加密后的文件和密钥文件缺一不可**
- **默认密码**：您可以自定义密码
- **文件类型**：支持多种文件格式


## 📝 注意事项

1. 虽然打包了多个平台的程序，但是我只测过 Windows
2. 加密之后的文件和密钥文件需要同时存在，丢了我也找不回
3. 密码是加密的核心

## 📝 未来计划

- 🛠️：修复 Golang 程序的小瑕疵
- ~~🎨：支持更多语言支持~~
