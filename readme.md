# Automated Human Mental Sensing

## 使用方法
- 在main.py中填入数据库的host, user, passwd
- 在chat.py中填入openai的api_key

## 目前实现
- 在time span中可以选择"morning", "afternoon", "evening", "night", "daytime", "whole day"
- 在sensor中可以选择"screen", "battery"
- 若sensor为"screen"，在metrics中可以选择"frequency","average_duration","total_duration"; 若sensor为"battery"，在metrics中可以选择"decrement","frequency"