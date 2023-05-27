# VMD-Lifting
VMD-Lifting is a fork of 'Lifting from the Deep' that outputs estimated 3D pose data to a VMD file

The authers of 'Lifting from the Deep' are Denis Tome', Chris Russell and Lourdes Agapito.
Please refer 'README-original.md' and http://visual.cs.ucl.ac.uk/pubs/liftingFromTheDeep/
for more information about the original 'Lifting from the Deep'.

This project is licensed under the terms of the GNU GPLv3 license. By using the software,
you are agreeing to the terms of the license agreement (see LICENSE file).

## 概要

写真から人のポーズを推定し、VMDフォーマットのモーション(ポーズ)データを出力するプログラムです。
ポーズ推定には Lifting from the Deep (https://github.com/DenisTome/Lifting-from-the-Deep-release)
のプログラムを使用しています。

## お試し

とりあえず使ってみたい方のために [Docker image](https://hub.docker.com/r/errnommd/vmd-lifting) を用意しました。
[Docker](https://www.docker.com/) がインストールされたPCで、例えば C:\test_photo に写真ファイルを置き、
Windows Powershell で次のコマンドを実行します。
写真は全身が写ったものを選んでください。ファイル名は例えば test1.jpg とします。

```
docker run -v c:\test_photo:/vmdl/test -it errnommd/vmd-lifting:latest
```

コンテナとファイルを共有するため、認証のダイアログが出ます。
ファイアウォールを通す設定が必要なこともあります。
なお、Docker imageが約2GBあるので、ダウンロードに時間がかかります。
"root@(文字列):/#" のように書かれたコマンドプロンプトが出たら準備完了です。
下記の手順で VMD-Lifting を実行します(先頭の#は入力しない)。

```
# cd /vmdl/applications
# python3 vmdlifting.py ../test/test1.jpg ../test/test1.vmd
```

次のようなメッセージが表示され、C:\test_photo に test1.vmd が作られます。
この VMD ファイルを MMD に読ませましょう。

```
pose estimation start
...
(略)
...
frame_num:  0
root@.......:/vmdl/applications#

```

終了するときは exit と入力します。

以上のように Docker で使い続けることもできますが、Docker版はGPUを使わない設定になっているので遅いです。
本格的に使用したい場合は、下記の手順でインストールを行い、GPUを有効にして使うことをお勧めします。

## VMD-Liftingの実行に必要なパッケージ
- python (3.x)
- [Tensorflow](https://www.tensorflow.org/)
- [OpenCV](http://opencv.org/)
- python-tk (Tkinter)
- PyQt5

## Linuxでのパッケージインストール手順

Ubuntu や Debian GNU/Linux の環境では、rootになって下記のコマンドを実行すると必要なものが揃います。

```
# apt-get install python3-pip
# pip3 install tensorflow-gpu
# apt-get install python3-opencv
# apt-get install python3-tk
# apt-get install python3-pyqt5
# apt-get install cmake
```

古いLinuxでは apt-get install python3-opencv が失敗することがあります。その場合、代わりに下記を実行します。

```
# pip3 install opencv-python
```

## Windowsでのパッケージインストール手順

Windowsの場合は次の手順で必要なものをインストールします。

- cygwin をインストール: https://cygwin.com/install.html

- https://www.tensorflow.org/install/install_windows に従って、CUDA、cuDNN、Python 3.6 をインストール

- cygwin の pythonでなく、上記でインストールしたpythonを使うように環境変数PATHを設定

- tensorflowをpipでインストール

`$ pip install  tensorflow-gpu`

- OpenCVをインストール

`$ pip install opencv-python`

- PyQt5をインストール

`$ pip install PyQt5`

## VMD-Liftingのセットアップ

- VMD-Liftingのアーカイブを展開して(あるいはgit cloneして)できたディレクトリに入り、setup.sh を実行します。
このスクリプトは必要なデータを取得し、外部ユーティリティをインストールします。
- (次に、Lifting from the Deep 本体の動作を確認したい場合は、application ディレクトリで demo.py を実行します。)

## 使用方法

application ディレクトリに入って vmdlifting.py を実行します。
コマンドライン引数として入力元画像/動画ファイル名と出力先VMDファイル名を指定します。

使用例:

```
./vmdlifting.py ../data/images/photo.jpg estimated.vmd
```
```
./vmdlifting.py movie.mp4 motion.vmd
```

コマンドライン引数とオプション:

```
usage: vmdlifting.py [-h] [--center] IMAGE_FILE VMD_FILE
```

- IMAGE_FILE: 入力元画像/動画ファイル名(JPEG, PNG, MP4など)
- VMD_FILE: 出力先VMDファイル名
- -h オプションでヘルプメッセージが表示されます
- --center オプションを付けると、出力されるVMDファイルにセンターボーンの位置が追加されます。(現状まだ不安定です)

## Lifting from the Deep について

Lifting from the Deep は、畳み込みニューラルネットワーク(CNN)を用いて、
単一のRGB画像から3Dのポーズ推定を行う手法(の論文)および、それを実装したプログラムです。
著者は Denis Tome', Chris Russell, Lourdes Agapito です。
詳しくはプロジェクトのWebページ ( http://visual.cs.ucl.ac.uk/pubs/liftingFromTheDeep/ )
の論文や動画を参照してください。

## ライセンスについて
(はじめに英語で書いたとおり)GNU GPLv3 licenseです。詳しくはLICENSEファイルを読んでください。

## 参考文献

D. Tome, C. Russell and L. Agapito. Lifting from the Deep: Convolutional 3D Pose Estimation
from a Single Image. In IEEE Conference on Computer Vision and Pattern Recognition (CVPR), 2017
