# Gym Membership Management System

This project is a web-based Gym Membership Management System developed using Flask and SQLite. It is designed to manage gym operations such as member records, trainer assignments, and payment tracking in an organized and efficient manner.

---

## Features

* Add, update, and delete member records
* Manage trainer details and assignments
* Track member payments
* Automatically calculate membership duration based on selected package
* Maintain a log of deleted members using database triggers
* Structured relational database with proper foreign key relationships

---

## Tech Stack

* Frontend: HTML, CSS
* Backend: Python (Flask)
* Database: SQLite
* Version Control: Git and GitHub

---

## Database Design

The system includes the following tables:

* members
* trainers
* payments
* deleted_members

Each member can be associated with a trainer, and payments are linked to members using foreign keys. This ensures proper data organization and consistency.

---

## Trigger Implementation

A database trigger is implemented to maintain a record of deleted members. Whenever a member is removed from the members table, their details are automatically stored in the deleted_members table along with a timestamp.

```sql id="y4c2te"
CREATE TRIGGER log_deleted_member
AFTER DELETE ON members
BEGIN
    INSERT INTO deleted_members (
        id, name, email, phone, package,
        start_date, end_date, trainer_id, deleted_at
    )
    VALUES (
        OLD.id, OLD.name, OLD.email, OLD.phone, OLD.package,
        OLD.start_date, OLD.end_date, OLD.trainer_id, datetime('now')
    );
END;
```

This helps in tracking and auditing deleted data effectively.

---

## Membership Packages

| Package | Duration  |
| ------- | --------- |
| Silver  | 6 months  |
| Gold    | 12 months |
| Diamond | 24 months |

The system automatically calculates the membership end date based on the selected package. 

---

## How to Run

1. Clone the repository:

```bash id="k7ip2c"
git clone https://github.com/LakshithaRadhakrishnan/Gym_Membership_Management.git
```

2. Navigate to the project folder:

```bash id="l0b3ya"
cd Gym_Membership_Management
```

3. Run the application:

```bash id="r1s6xt"
python app.py
```

4. Open the application in your browser:

```
http://127.0.0.1:5000/
```

---

## Project Structure

```
gym-member/
│
├── app.py
├── gym.db
├── templates/
├── static/
└── README.md
```

---

## Future Enhancements

* User authentication and role-based access
* Dashboard with analytics and reports
* Notification system for membership expiry
* Integration with cloud database

---

## Author

Lakshitha
