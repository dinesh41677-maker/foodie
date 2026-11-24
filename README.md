# Foodie - Food Delivery Website (Flask + MySQL)

## Run it (Windows)

1. Install Python 3.10+ and MySQL Server 8. Start MySQL.
2. Open PowerShell inside this folder, then:

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

3. Open the `.env` file and set `DB_PASSWORD` to your MySQL root password.
4. Create the database, tables, sample food and the admin account:

```powershell
python setup_db.py
```

5. Start the website:

```powershell
python app.py
```

6. Open http://127.0.0.1:5000

## Admin login
Email: `admin@foodie.com`  Password: `Admin@12345` (change them in `.env` BEFORE step 4, or change the password later in Profile).
Admin panel: http://127.0.0.1:5000/admin

## Food photos
The 14 sample foods expect these files in `static/uploads/foods/`:
veg-biryani.jpg, paneer-biryani.jpg, gobi-fried-rice.jpg, veg-meals.jpg, dosa.jpg, parotta.jpg,
paneer-butter-masala.jpg, chicken-biryani.jpg, mutton-biryani.jpg, chicken-65.jpg,
chicken-fried-rice.jpg, egg-roll.jpg, fish-fry.jpg, chicken-meals.jpg

Download free photos from pexels.com or unsplash.com and save them with these exact names.
Until then an orange plate icon is shown. You can also upload photos from Admin > Foods > Edit.

## Tests (no MySQL needed)
```powershell
pytest
```

## Start over
`python setup_db.py --reset` deletes everything and rebuilds the sample data.

## Not included (be aware)
- Online payment gateway: payment method is only recorded (pay on delivery).
- Emails / SMS notifications.
- Login attempt limit is kept in memory (resets on restart).
