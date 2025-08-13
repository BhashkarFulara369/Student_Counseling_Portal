# 🎓 Student Counseling Portal

A full-stack Django-based web application designed to streamline the student counseling process for educational institutions. This portal handles seat allocation, branch preferences, payment verification, and offer letter generation — all in one secure and user-friendly platform.

---

## 🚀 Key Features

### 🔐 Role-Based Authentication
- Separate login flows for **students** and **staff admins**
- Secure session management using Django AllAuth

### 📝 Student Workflow
Students follow a guided, multi-step process:
- Personal Information Submission
- Educational Details Entry
- Branch Preference Filling
- Receipt Upload for Payment Verification
- Offer Letter Download (post-verification)

### 🧑‍💼 Admin Dashboard
Staff admins have access to a powerful control panel:
- View student rankings and branch choices
- Manually allocate branches
- Toggle acceptance status
- Verify uploaded payment receipts
- Generate and download official offer letters

### 📄 Offer Letter Generation
- Professionally styled PDF letters
- Includes institute logo, signature, and student details
- Downloadable by both students and staff

### 📤 Receipt Uploads
- Students can upload payment receipts (PDF, JPG, PNG)
- Stored securely in the media directory
- Verified manually by staff via the admin panel

---


## 🎥 Demo Video

Want to see the portal in action?  
```markdown
<video src="demo/student_counseling_portal_demo.mp4" controls width="800">
</video>
```


## 🛠️ Tech Stack

| Layer        | Technology         |
|--------------|--------------------|
| Backend      | Django 5.2         |
| Frontend     | Bootstrap 5        |
| PDF Engine   | ReportLab          |
| Auth System  | Django AllAuth     |
| Database     | SQLite (default) — easily swappable with PostgreSQL |

---

## 📁 Folder Structure
```
student_counseling_portal/
├── manage.py
├── requirements.txt
├── db.sqlite3
├── media/
│   └── receipts/
├── static/
│   └──/images
├── templates/
│   └── ...
├── student_portal/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── ...
├── staff_dashboard/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── ...
├── offer_letter/
│   ├── __init__.py
│   ├── pdf_generator.py
│   └── ...
├── student_counseling_portal/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
```


## ⚡ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/BhashkarFulara369/student_counseling_portal.git
cd student_counseling_portal
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply Migrations
```bash
python manage.py migrate
```

### 5. Create a Superuser (for Overall access)
```bash
python manage.py createsuperuser
```

### 6. Run the Development Server
```bash
python manage.py runserver
```

### 7. Access the Portal
- Student Portal: `http://localhost:8000/`
- Admin Dashboard: `http://localhost:8000/admin-panel/`

---

**Note:**  
- For PDF generation, ensure ReportLab is installed (included in `requirements.txt`).
- Uploaded receipts and generated offer letters are stored in the `media/` directory.
- To use PostgreSQL or another database, update `settings.py` accordingly.
- For email verification, configure SMTP settings in `settings.py` if required.

## 🌟 Future Enhancements

- **Automated Branch Allocation:** Implement algorithms for automatic seat and branch allocation based on merit and preferences.
- **Real-Time Notifications:** Integrate email/SMS notifications for application status updates and important deadlines.
- **Analytics Dashboard:** Provide visual analytics for admin users to track counseling trends and student statistics.
- **Multi-Institute Support:** Extend platform to support multiple institutions with customizable workflows.
- **Document Verification Automation:** Use OCR and AI to automate verification of uploaded documents and receipts.
- **Mobile App Integration:** Develop companion mobile apps for students and staff for easier access.
- **Multi-Language Support:** Add localization for regional languages to improve accessibility.
- **Payment Gateway Integration:** Enable online fee payments and instant verification.
- **Bulk Data Import/Export:** Allow admins to import/export student data and counseling results in CSV/Excel formats.
- **Enhanced Security:** Add two-factor authentication and advanced access controls for sensitive operations.

## 🤝 Contributing

I welcome contributions! To get started:

1. Fork the repository and create your branch (`git checkout -b feature-name`)
2. Make your changes and commit them (`git commit -m 'Add new feature'`)
3. Push to your fork (`git push origin feature-name`)
4. Open a pull request describing your changes

Please ensure your code follows the existing style and includes relevant tests or documentation. For major changes, open an issue first to discuss your ideas.

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

_Made with ❤️ by [BhashkarFulara](https://github.com/BhashkarFulara369)_

