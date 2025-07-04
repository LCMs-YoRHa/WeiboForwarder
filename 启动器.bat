@echo off
chcp 65001 >nul
echo =======================================
echo         微博RSS长图生成器
echo =======================================
echo.

:menu
echo 请选择操作：
echo 1. 生成最新微博长图
echo 2. 列出所有微博
echo 3. 选择特定微博生成
echo 4. 演示模式（无需网络）
echo 5. 退出
echo.
set /p choice=请输入选项 (1-5): 

if "%choice%"=="1" goto latest
if "%choice%"=="2" goto list
if "%choice%"=="3" goto select
if "%choice%"=="4" goto demo
if "%choice%"=="5" goto exit
echo 无效选项，请重新选择！
echo.
goto menu

:latest
echo.
echo 🚀 正在生成最新微博长图...
python Weibo.py
if %errorlevel% equ 0 (
    echo.
    echo ✅ 生成完成！
    echo 📁 请查看 outputs 目录
) else (
    echo.
    echo ❌ 生成失败，请检查错误信息
)
echo.
pause
goto menu

:list
echo.
echo 📋 获取微博列表...
python Weibo.py --list
echo.
pause
goto menu

:select
echo.
echo 📋 先显示微博列表...
python Weibo.py --list
echo.
set /p index=请输入要生成的微博索引号 (从0开始): 
echo.
echo 🚀 正在生成第 %index% 条微博长图...
python Weibo.py --index %index%
if %errorlevel% equ 0 (
    echo.
    echo ✅ 生成完成！
    echo 📁 请查看 outputs 目录
) else (
    echo.
    echo ❌ 生成失败，请检查错误信息
)
echo.
pause
goto menu

:demo
echo.
echo 🎯 演示模式 - 使用内置数据（无需网络连接）
echo.
echo 请选择演示操作：
echo 1. 查看演示微博列表
echo 2. 生成第1条演示微博（『致不灭的你』）
echo 3. 生成第2条演示微博（『棋魂』插画合集）
echo 4. 返回主菜单
echo.
set /p demo_choice=请输入选项 (1-4): 

if "%demo_choice%"=="1" goto demo_list
if "%demo_choice%"=="2" goto demo_1
if "%demo_choice%"=="3" goto demo_2
if "%demo_choice%"=="4" goto menu
echo 无效选项！
goto demo

:demo_list
echo.
echo 📋 演示微博列表...
python Weibo.py --demo --list
echo.
pause
goto demo

:demo_1
echo.
echo 🚀 正在生成演示微博1...
python Weibo.py --demo --index 0 --output "演示-致不灭的你.jpg"
if %errorlevel% equ 0 (
    echo.
    echo ✅ 生成完成！文件: 演示-致不灭的你.jpg
    echo 📁 请查看 outputs 目录
) else (
    echo.
    echo ❌ 生成失败，请检查错误信息
)
echo.
pause
goto demo

:demo_2
echo.
echo 🚀 正在生成演示微博2...
python Weibo.py --demo --index 1 --output "演示-棋魂插画合集.jpg"
if %errorlevel% equ 0 (
    echo.
    echo ✅ 生成完成！文件: 演示-棋魂插画合集.jpg
    echo 📁 请查看 outputs 目录
) else (
    echo.
    echo ❌ 生成失败，请检查错误信息
)
echo.
pause
goto demo

:exit
echo.
echo 👋 再见！
timeout /t 2 >nul
exit
