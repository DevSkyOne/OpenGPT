<!-- Template for readme used: https://github.com/othneildrew/Best-README-Template -->
<a name="readme-top"></a>

<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]


<!-- PROJECT LOGO -->
<br />
<div align="center">
<h3 align="center">OpenGPT</h3>

  <a href="https://github.com/CoasterFreakDE/OpenGPT">
    <img src="images/opengpt-nobg.png" alt="Logo" width="80" height="80">
  </a>

  <p align="center">
    Open Source ChatGPT-4 discord bot
    <br />
    <br />
    <a href="https://github.com/CoasterFreakDE/OpenGPT/issues">Report Bug</a>
    ·
    <a href="https://github.com/CoasterFreakDE/OpenGPT/issues">Request Feature</a>
  </p>
</div>

<!-- ABOUT THE PROJECT -->

## About The Project

OpenGPT Discord Bot is an interactive Discord bot built to communicate with OpenAI's GPT-3.5-Turbo and GPT-4 API. This project aims to bring the power and convenience of ChatGPT to Discord servers, allowing users to engage in conversations, ask questions, or seek information from a highly advanced AI language model.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


### Features

Interact with ChatGPT-4 by simply mentioning the bot using @OpenGPT or replying to a recent message from the bot.
Accessible and user-friendly, with a daily limit of 100 Credits (equivalent to ~10 cents) per user to manage API costs.

Invite the official bot to your server with ease using this link: [Official discord bot invite](https://discord.com/api/oauth2/authorize?client_id=646411900267135004&permissions=274877975552&scope=bot%20applications.commands)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

* [![Python][Python]][Python-url]
* [![discord4py][discord4py]][discord4py-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- GETTING STARTED -->

## Getting Started

To get a local copy up and running follow these simple steps.

### Prerequisites

You need the following software to run this plugin:

* Python 3.9+
* [OpenAI Account with billing method](https://platform.openai.com/account/usage)

### Installation

1. Clone the repository
2. Use `pip install -r requirements.txt` to install all dependencies
3. Rename `.env.example` to `.env` and edit your openai api and discord bot token
4. Start the bot with `python opengpt.py` 

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ROADMAP -->

## Roadmap

- [ ] Threads
- [ ] File Support
- [ ] Image Support (GPT-4 api added image support)

See the [open issues](https://github.com/CoasterFreakDE/OpenGPT/issues?q=is%3Aissue+is%3Aopen+sort%3Aupdated-desc) for a full
list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->

## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any
contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also
simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Branch naming

* `feature/` for new features
* `fix/` for bug fixes
* `docs/` for documentation changes
* `refactor/` for code changes that neither fixes a bug nor adds a feature
* `style/` for formatting, missing semi colons, etc; no code change
* `test/` for everything related to testing
* `chore/` for updating build tasks, package manager configs, etc; no production code change

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->

## License

Distributed under the MIT License. See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


## Support & Sponsorship

The OpenGPT Discord Bot project is actively maintained and improved. Your support and sponsorship on GitHub directly contribute to the ongoing development and maintenance of the project. By sponsoring, you help ensure that the bot continues to provide users with a seamless and engaging ChatGPT-4 experience on Discord.

Sponsor the project here: [GitHub Sponsorship Page](https://github.com/sponsors/CoasterFreakDE)

Please don't hesitate to open issues or submit pull requests for any improvements or bug fixes. Your contributions are always welcome!



<!-- CONTACT -->

## Contact

Project Link: [https://github.com/CoasterFreakDE/OpenGPT](https://github.com/CoasterFreakDE/OpenGPT)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->

## Acknowledgments

* [GitHub Emoji Cheat Sheet](https://www.webpagefx.com/tools/emoji-cheat-sheet)
* [Img Shields](https://shields.io)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[contributors-shield]: https://img.shields.io/github/contributors/CoasterFreakDE/OpenGPT.svg?style=for-the-badge
[contributors-url]: https://github.com/orgs/CoasterFreakDE/OpenGPT/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/CoasterFreakDE/OpenGPT.svg?style=for-the-badge
[forks-url]: https://github.com/CoasterFreakDE/OpenGPT/network/members
[stars-shield]: https://img.shields.io/github/stars/CoasterFreakDE/OpenGPT.svg?style=for-the-badge
[stars-url]: https://github.com/CoasterFreakDE/OpenGPT/stargazers
[issues-shield]: https://img.shields.io/github/issues/CoasterFreakDE/OpenGPT.svg?style=for-the-badge
[issues-url]: https://github.com/CoasterFreakDE/OpenGPT/issues
[license-shield]: https://img.shields.io/github/license/CoasterFreakDE/OpenGPT.svg?style=for-the-badge
[license-url]: https://github.com/orgs/CoasterFreakDE/OpenGPT/main/LICENSE
[Python]: https://img.shields.io/badge/Language-Python-green
[Python-url]: https://www.python.org/
[discord4py]: https://img.shields.io/badge/Framework-discord4py-blue
[discord4py-url]: https://github.com/mccoderpy/discord.py-message-components
