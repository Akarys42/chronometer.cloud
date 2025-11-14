# chronometer.cloud

Cloud-Synchronized Chronometers
Live demo → https://chronometer.cloud/

# Overview

Chronometer.cloud is a web application that lets users create, run and synchronize chronometers (stopwatches/timers) across devices via the cloud. The idea is to provide a lightweight, accessible tool that works in the browser, stores data in a backend, and keeps multiple clients in sync.
It’s built using a frontend (Vue/Nuxt) and a backend (FastAPI/Python) with a ready‐to‐go Docker setup.

# Motivation

This projet was born out of a desire to provide high-quality timers for TCG tournaments, ready to be displayed inside the venue, and always accessible for staff members.

# Features

- Create and manage multiple chronometers simultaneously

- Start, pause, resume, reset each chronometer

- Synchronization across multiple browser tabs/devices (via backend)

- Cloud persistence: your timing data remains available if you switch device

- Responsive UI: works on desktop and mobile browsers

- Open Source: MIT licensed

- Ready to be displayed on large screens

# Tech Stack

Frontend: Vue.js / Nuxt (TypeScript)

Backend: Python / FastAPI

Database: MongoDB

Deployment: Docker & Kubernetes in production

# Contributing

Contributions are warmly welcome. Whether it’s a bug fix, feature suggestion, UI improvement or documentation update, please feel free to open an issue or a pull request.
Before contributing:

- Fork the repo

- Create a new branch

- Ensure your changes are tested and linted

- Write a clear PR description
