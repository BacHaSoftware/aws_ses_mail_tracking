
<a name="readme-top"></a>

<!-- PROJECT DETAILS -->
<br />
<div align="center">
  <a href="https://github.com/BacHaSoftware/aws_ses_mail_tracking">
    <img src="/bhs_aws_ses_mail_tracking/static/description/icon.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">AWS SES Mail Tracking</h3>

  <p align="center">
    Proper redirection of fetched replies of emails sent from Odoo through SES outgoing.
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact-us">Contact us</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

<div align="left">
  <a href="https://github.com/BacHaSoftware/aws_ses_mail_tracking">
    <img src="/bhs_aws_ses_mail_tracking/static/description/banner.gif" alt="Setting">
  </a>
</div>

#### Key Features:

🌟 <code>Add Field</code>: Add field SES Message-ID to record new message-id when sending via SES outgoing mail server. Use this field to track if email was sent via SES outgoing mail server instead of the old message-id field.

🌟 <code>Tracking Email</code>: Allow to track bounce and reply if emails are sent via SES outgoing mail server. Do not affect tracking of emails sent via other mail server.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- GETTING STARTED -->
## Getting Started

<!-- PREREQUISTES  
### Prerequisites

This module needs the Python library <code>slackclient</code>, <code>html-slacker</code>, otherwise it cannot be installed and used. Install them through the command
  ```sh
  sudo pip3 install slackclient
  sudo pip3 install html-slacker
  ```
 -->
### Installation

1. Install module  <code>bhs_aws_ses_mail_tracking</code>
2. Configure outgoing mail server
3. Configure incoming mail server: The email used to configure incoming mail server must be the email that has been configured as mail catchall of your domain.
4. Configure alias domain: After installing module, alias domain yourcompany.com is automatically generated, you need to change it to your real domain.
5. Configure alias: Name of alias must match the email configured at incoming mail server, Aliased Model is Mass Mailing and Record Thread ID is the id of mass mailing which is automatically generated after installing module.

When you send a mass mailing or marketing automation campaign, configure send from and reply to is the email configured at incoming mail server.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->
## Usage

When sending emails via outgoing mail server SES, message-id of the email is changed, lead to not being able to track replies and bounces of those emails. This module provides a solution to that problem.


#### Featured Highlight:

🌟 <code>Add Field</code>: Add field SES Message-ID to record new message-id when sending via SES outgoing mail server. Use this field to track if email was sent via SES outgoing mail server instead of the old message-id field.

🌟 <code>Tracking Email</code>: Allow to track bounce and reply if emails are sent via SES outgoing mail server. Do not affect tracking of emails sent via other mail server.


<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT US-->
## Contact us
Need assistance with setup or have any concerns? Contact Bac Ha Software directly for prompt and dedicated support:
<div align="left">
  <a href="https://github.com/BacHaSoftware">
    <img src="/bhs_aws_ses_mail_tracking/static/description/imgs/logo.png" alt="Logo" height="80">
  </a>
</div>

📨 odoo@bachasoftware.com

🌍 [https://bachasoftware.com](https://bachasoftware.com)

[![WEBSITE][website-shield]][website-url] [![LinkedIn][linkedin-shield]][linkedin-url]

Project Link: [https://github.com/BacHaSoftware/aws_ses_mail_tracking](https://github.com/BacHaSoftware/aws_ses_mail_tracking)


<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[license-url]: https://github.com/BacHaSoftware/aws_ses_mail_tracking/blob/17.0/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/company/bac-ha-software
[website-shield]: https://img.shields.io/badge/-website-black.svg?style=for-the-badge&logo=website&colorB=555
[website-url]: https://bachasoftware.com