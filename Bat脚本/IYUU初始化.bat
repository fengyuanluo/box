@echo off
CHCP 65001
rem 申请管理员权限
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"

if '%errorlevel%' NEQ '0' (
    echo 请求管理员权限...
    goto UACPrompt
) else ( goto gotAdmin )

:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"

    "%temp%\getadmin.vbs"
    exit /B

:gotAdmin
    if exist "%temp%\getadmin.vbs" ( del "%temp%\getadmin.vbs" )
    pushd "%CD%"
    CD /D "%~dp0"

setlocal

rem 1. 获取脚本所在目录
set "CURRENT_DIR=%~dp0"
set "MYSQL_DIR=%CURRENT_DIR%MySQL"

rem 2. 将 MySQL 和 PHP 所在目录永久添加到环境变量
set "MYSQL_BIN_DIR=%MYSQL_DIR%\bin"
set "PHP_DIR=%CURRENT_DIR%PHP"

echo 正在检查环境变量...
set "PATH_BACKUP=%PATH%"
setx PATH "%MYSQL_BIN_DIR%;%PATH%" /M > nul
if %errorlevel% neq 0 (
    echo 无法将 MySQL 路径添加到环境变量中
) else (
    echo MySQL 路径已添加到环境变量中
    set "PATH=%MYSQL_BIN_DIR%;%PATH%"
)

setx PATH "%PHP_DIR%;%PATH%" /M > nul
if %errorlevel% neq 0 (
    echo 无法将 PHP 路径添加到环境变量中
) else (
    echo PHP 路径已添加到环境变量中
    set "PATH=%PHP_DIR%;%PATH%"
)

where mysql > nul
if %errorlevel% neq 0 (
    echo 无法在环境变量中找到 MySQL
    set "PATH=%PATH_BACKUP%"
) else (
    echo MySQL 路径已成功添加到环境变量中
)

rem 3. 安装和初始化 MySQL

echo 正在检查 MySQL 安装...
net start mysql > nul 2>&1
if %errorlevel% neq 0 (
    echo MySQL 未安装或未启动
    mkdir "%MYSQL_DIR%"
	mysqld --install
    mysqld --initialize-insecure
    net start mysql
) else (
    echo MySQL 已安装并运行
)

rem 4. 初始化 MySQL，创建一个数据库
set /p DB_NAME="请输入数据库名: "
set /p DB_USER="请输入数据库用户名: "
set /p DB_PASS="请输入数据库密码: "

mysql -u root -e "CREATE USER IF NOT EXISTS '%DB_USER%'@'localhost' IDENTIFIED BY '%DB_PASS%'; CREATE DATABASE IF NOT EXISTS `%DB_NAME%`; GRANT ALL PRIVILEGES ON `%DB_NAME%`.* TO '%DB_USER%'@'localhost';"

rem 5. 创建 php.ini 配置文件
if not exist "%PHP_DIR%\php.ini" (
    echo 正在创建 php.ini 文件...
    copy "%PHP_DIR%\php.ini-development" "%PHP_DIR%\php.ini"
) else (
    set /p OVERWRITE="php.ini 文件已存在,是否覆盖(Y/N)? "
    if /i "%OVERWRITE%"=="Y" copy "%PHP_DIR%\php.ini-development" "%PHP_DIR%\php.ini"
)

rem 6. 为 PHP 安装并启用 pdo_mysql 扩展
rem 7. 将扩展目录指定为项目/PHP/ext
echo extension_dir="%CURRENT_DIR%PHP\ext" >> "%PHP_DIR%\php.ini"
echo extension=curl >> "%PHP_DIR%\php.ini"
echo extension=fileinfo >> "%PHP_DIR%\php.ini"
echo extension=gd >> "%PHP_DIR%\php.ini"
echo extension=mbstring >> "%PHP_DIR%\php.ini"
echo extension=exif >> "%PHP_DIR%\php.ini"
echo extension=mysqli >> "%PHP_DIR%\php.ini"
echo extension=openssl >> "%PHP_DIR%\php.ini"
echo extension=pdo_mysql >> "%PHP_DIR%\php.ini"
echo extension=pdo_sqlite >> "%PHP_DIR%\php.ini"
echo extension=sockets >> "%PHP_DIR%\php.ini"
echo extension=sodium >> "%PHP_DIR%\php.ini"
echo extension=sqlite3 >> "%PHP_DIR%\php.ini"
echo extension=zip >> "%PHP_DIR%\php.ini"


rem 8. 设置环境变量用于 Phinx 迁移
set DB_HOST=localhost
set DB_DATABASE=%DB_NAME%
set DB_USERNAME=%DB_USER%
set DB_PASSWORD=%DB_PASS%
set DB_PORT=3306

rem 9. 执行 Phinx 迁移
php vendor\bin\phinx migrate -e development

echo 初始化完成!

endlocal