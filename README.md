<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Thanks again! Now go create something AMAZING! :D
***
***
***
*** To avoid retyping too much info. Do a search and replace for the following:
*** github_username, repo_name, twitter_handle, email, project_title, project_description
-->


<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary><h2 style="display: inline-block">Table of Contents</h2></summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

This is a code repository for backend of Work Around project, that was created as solution of Hackprague 2021 challenge.
As part of the solution was created [frontend](https://github.com/borisrakovan/workaround-frontend) that leverages
features of this backend.

Work Around is a platform for people who have a place of their own (flat, house, ...) and would like to try living
somewhere else for a change. In the age of COVID, working at home has become more and more common. Work Around is
giving people the opportunity to work around the world, having adventures while working the same remote job
they did back home.

### How it works
Adventurer who joins this platform will give his property into the program, giving location, features, etc.
Then they can apply for participation with this property. They will then fill out their preferred destinations
and other preferences. After that, our algorithm will match that person with other adventurers who have matching
interests creating a chain of house/flat swaps. This gives each person their next destination for temporary living.

### Built With

* [Django](https://www.djangoproject.com/)
* [Graphene](https://graphene-python.org/)


<!-- GETTING STARTED -->
## Getting Started

### Prerequisites
  ```sh
  sudo apt-get install libgdal-dev
  ```

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/Learneron/web-app.git https://github.com/osvalros/work-around-backend.git
   ```
2. Install libraries
  ```sh
  pip install -r requirements
  ```
3. Run development server
   ```sh
   python manage.py runserver
   ```
4. Go to localhost:8000
