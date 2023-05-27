# VMD-Mediapipe
VMD-Mediapipe is a fork of 'VMD-Lifting' that outputs estimated 3D pose data to a VMD file

This project is licensed under the terms of the GNU GPLv3 license. By using the software,
you are agreeing to the terms of the license agreement (see LICENSE file).

## 概要

写真から人のポーズを推定し、VMDフォーマットのモーション(ポーズ)データを出力するプログラムです。
ポーズ推定には Mediapipe (https://developers.google.com/mediapipe/)
を使用しています。

## VMD-Mediapipeの実行に必要なパッケージ
- python (3.x)
- [Mediapipe](https://developers.google.com/mediapipe/)
- [OpenCV](http://opencv.org/)
- scipy
- PyQt6

## Linuxでのパッケージインストール手順

Ubuntu や Debian GNU/Linux の環境では、rootになって下記のコマンドを実行すると必要なものが揃います。

```
# apt-get install python3-pip
# pip3 install mediapipe
# apt-get install python3-opencv
# apt-get install python3-pyqt6
# apt-get install cmake
```

古いLinuxでは apt-get install python3-opencv が失敗することがあります。その場合、代わりに下記を実行します。

```
# pip3 install opencv-python
```

## VMD-Mediapipeのセットアップ

- VMD-Mediapipeのアーカイブを展開して(あるいはgit cloneして)できたディレクトリに入り、setup.sh を実行します。
このスクリプトは必要なデータを取得し、外部ユーティリティをインストールします。


## 使用方法

application ディレクトリに入って vmd_mediapipe.py を実行します。
コマンドライン引数として入力元画像/動画ファイル名と出力先VMDファイル名を指定します。

使用例:

```
./vmd_mediapipe.py ../data/images/photo.jpg estimated.vmd
```
```
./vmd_mediapipe.py movie.mp4 motion.vmd
```

コマンドライン引数とオプション:

```
usage: vmd_mediapipe.py [-h] [--center] IMAGE_FILE VMD_FILE
```

- IMAGE_FILE: 入力元画像/動画ファイル名(JPEG, PNG, MP4など)
- VMD_FILE: 出力先VMDファイル名
- -h オプションでヘルプメッセージが表示されます
- --center オプションを付けると、出力されるVMDファイルにセンターボーンの位置が追加されます。(現状まだ不安定です)


