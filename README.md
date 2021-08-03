<p align="center">
    <img src="https://hyenabot.xyz/images/logo.png" width="311.25" height="270"/>
</p>

### **‚ùî Hyena Bot**

A useful bot that will bring great fun to your server! Configure Moderation, Logging, Starboard, Fun commands, Welcome/Leave messages etc.

- All sorts of moderation commands, yeh pls ban 7 year old candy crush players.
- God tier auto Moderation kekwnt.
- Moderation command logs & regular server Mod Logs

### ➜ Stats

[![](https://top.gg/api/widget/790892810243932160.svg)](https://top.gg/bot/790892810243932160)

### ➜ How to colaborate here

> For any doubts here, contact Donut#4427 please.

Step 1: Fork & Clone the repository

```sh
$ git clone link-to-my-forked-repository.git hyenabot # usually link will be https://github.com/YourUserName/HyenaDev
$ cd hyenabot
```

➜ How to install discord.py 2.0a

- Firstly, setup a virtual environment

```sh
$ pip install virtualenv
$ cd src
$ virtualenv venv
$ ./venv/bin/activate # windows
$ source ./venv/bin/activate # macos or linux
```

- Then install the 2.0a

```sh
$ git clone https://github.com/Rapptz/discord.py discord.py
$ cd discord.py
$ pip install -U .[voice]
```

Step 2: Checkout a new branch

```sh
$ git checkout -b my-new-feature
```

Step 3: Code the feature
<br/>
Pick a feature from the Issues and code it
<br/>
Am i supposed to tell you how to do this one too?

Step 4: Commit the feature

```sh
$ git commit -m "define your feature here"
```

- For noobs like you (and me) who don't know how to write a commit message:
  <br/>
- [How to write a proper commit message](https://gist.github.com/develar/273e2eb938792cf5f86451fbac2bcd51)

Step 5: Push the feature

```sh
$ git push origin my-new-feature # branch name should be same as the one you checked out
```

Step 6: Create a pull request

- Go to the your forked repository
- A button like this will appear, click on it:
  <br/><br/>
  ![Button](https://i.ibb.co/jhQNdYX/Screenshot-2021-07-30-at-2-45-15-PM.png)
  <br/><br/>
- Create a pull request like this:
  <br/><br/>
  ![Create a pull request](https://i.ibb.co/4WSCYnZ/Screenshot-2021-07-30-at-2-45-43-PM.png)
  <br/><br/>
- Then Donut or Div will merge the pull request after reviewing

### ➜ How to add your forked repository to the #github channel of Hyena's server

- Step 1: Go to your repository
- Step 2: Click on `Settings` -> `Webhooks` -> `Add webhook`
- Step 3: Fill in `Payload URL with`

```
https://discord.com/api/webhooks/833230915357376532/A00W00rhhF40NzDVG8lpjTAWkFRygBUWWuGzhACkTDl49PuaOQrQhLSPSolQYkJOb38p/github
```

- Step 4: Change content type to `application/json`
- Step 5: Change `Which events would you like to trigger this webhook?` to `Send me everything.`
- Step 6: Let the rest be the same and click on `Add webhook`, and you're done