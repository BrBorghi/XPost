# xpost - a simple streamlit app to post on X

## Prerequisites

- You must have a [X Developer Portal](https://developer.x.com/) account. A free account is enough.
- In this portal, you must declare a project app with **Read and Write permissions** (warning: the default is read only) to get correct *Consumer keys* and *Authentication Tokens*.

## Features

`xpost` let you edit a post for your X account in a simple page in your web browser. Optionally, you can quote an existing post by entering its URL or its Id. `xpost` monitors and displays the number of characters you typed. A customizable maximum text length is enforced. Click on the "Post on X" button and you're done. That's all.

`xpost` is protected by a password. You can log out at any moment.

The password and the X secrets are declared in a [streamlit secrets file](https://docs.streamlit.io/develop/concepts/connections/secrets-management). See `secrets_example.toml` for an example.

Some parameters are declared in the `config.toml` file. These parameters can be declared as well in the secrets file. The paramaters in the secrets file overwrite the paramaters in the config file.

## Local deployment

### Installation
- Clone the repo in a folder.
- Create a python3 virtual environment using your favorite method.
- In the folder, run `pip install -r requirements.txt`
- Copy the secrets file example: `mkdir -p .streamlit && cp secrets_example.toml .streamlit/secrets.toml`
- Edit `.streamlit/secrets.toml` to set up your X credentials.

### Running the app

`streamlit run xpost.py`

A new tab will open in your default browser with the xpost app. Streamlit usually runs a server on port 8501. Check the streamlit documentation if you want to change the port.

## Cloud deployment

`xpost` is ready to be deployed in the *[Streamlit Community Cloud](https://streamlit.io/cloud)* in the free tier. You can deploy directly from this Github repo. When creating the app in the community cloud, you must set up your secrets by means of the Community Cloud Secrets Management console.

## Credits
- Thank you to some alternatives. I found that *[Typefully](https://typefully.com/)* is too expensive for my needs. I tried to install locally the free editions of *[Postiz](https://postiz.com/)* and *[Mixpost](https://mixpost.app/)* to realize that each take more than 1 Go space on my disk - too heavy for my needs.
- Thank you to *[Grok](https://grok.com)* which, under my tight supervision, coded most of it.

