# FlightsFilter

## Introduction

**FlightsFilter** is a core microservice of the **Travel-Booking-Framework** that provides an advanced search and filtering system for flights. This service is developed using **Django** and **Elasticsearch**, allowing for fast and efficient flight searches based on multiple criteria.

## Features

- **Flight Search**: Search flights based on origin, destination, date, and other parameters.
- **Advanced Filters**: Filter flights by price, duration, departure time, and other factors.
- **Flight Management**: Add, update, and delete flight information.

## Prerequisites

- **Python 3.x**
- **Django**
- **Elasticsearch**

## Installation and Setup

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/Travel-Booking-Framework/FlightsFilter.git
   cd FlightsFilter
   ```

2. **Create and Activate a Virtual Environment**:

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use: venv\\Scripts\\activate
    ```

3. **Install Dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

4. **Setup Elasticsearch**: Ensure that **Elasticsearch** is installed and running on your system. Update the Django settings (`settings.py`) with the correct Elasticsearch configuration.


## Project Structure

- **FFilter/**: Contains the core settings and configurations for Django.
- **FlightsFilter/**: Manages flight-related operations and filtering functionalities.
- **Class-Diagram/**: Provides class diagrams for understanding the project architecture.

## Contribution Guidelines

We welcome contributions from the community! To contribute:

1. **Fork** the repository.
2. **Create a new branch** for your feature or bug fix.
3. **Commit** your changes.
4. **Submit a Pull Request**.


## Additional Notes

- **Create a Superuser**: To create an admin account, use the command:
  ```bash
  python manage.py createsuperuser
  ```

- **GraphQL Support**: This project includes GraphQL capabilities, which can be accessed at `/graphql/`.