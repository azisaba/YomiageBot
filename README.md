# YomiageBot
DiscordのメッセージをVoiceChannelで読み上げてくれるBot
## Environment
Python 3.9
## Installation
1. 任意のディレクトリを作成します  
2. レポジトリをクローンします  
```sh
git clone https://github.com/azisaba/YomiageBot.git
```  
3. config.ymlを1で作成したディレクトに作成します  
config.yml
```yml
listener_token: LISTENER_TOKEN
speaker_token:
  - SPEAKER_TOKEN_1
  - SPEAKER_TOKEN_2
  ...
```  
トークンは複数登録することが可能です  
4. Google-Text-to-Speechのトークンを用意して、1で作成したディレクトリに保存してください  
5. スタートアップスクリプトを用意します  
start.sh  
```sh
# setting
export GOOGLE_APPLICATION_CREDENTIALS="TOKEN_PATH"
# start
python3 /your/created/directory/YomiageBot/script/main.py /your/created/directory/
```   
ワーキングディレクトリを引数として渡してください。コンフィグファイルは自動で探します  
ファイル構造  
```
your_created_directory
 |- YomiageBot
  |- script ..
 |- config.yml
 |- start.sh
```  