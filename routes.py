from flask import Blueprint, render_template, request, redirect, url_for, flash, session,jsonify
from flask_mail import Message
from extensions import mail  # Import the mail instance
import sqlite3
import logging
from urllib.parse import quote_plus
routes_blueprint = Blueprint('routes', __name__)

####
def get_db_connection():
    conn = sqlite3.connect('secretsanta.db')
    conn.row_factory = sqlite3.Row
    return conn

####
@routes_blueprint.route("/")
def index():
    return render_template("index.html")

####
@routes_blueprint.route("/select-staff", methods=["GET"])
def select_staff():
    try:
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Fetch all staff names
        cursor.execute("SELECT name FROM staff")
        rows = cursor.fetchall()

        # Convert rows to a list of dictionaries
        staff = [{"name": row["name"]} for row in rows]
        print(f"Staff list retrieved: {staff}")

        return render_template("select-staff.html", staff=staff)

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        flash("Unable to fetch staff. Please try again later.", "error")
        return redirect(url_for("routes.home"))

    finally:
        if 'conn' in locals():
            conn.close()


####
@routes_blueprint.route("/register-email", methods=["POST"])
def register_email():
    conn = sqlite3.connect("secretsanta.db")
    cursor = conn.cursor()

    name = request.form.get("name")
    phone = request.form.get("phone")
    email = request.form.get("email")
    confirm_email = request.form.get("confirm_email")

    # Validate email confirmation
    if email != confirm_email:
        return render_template(
            "confirm-phone.html",
            name=name,
            last_digits=phone[-4:],
            error="Email addresses do not match.",
        )

    try:
        # Update staff email and phone details
        cursor.execute(
            "UPDATE staff SET phone = ?, email = ? WHERE name = ?",
            (phone, email, name),
        )
        conn.commit()

        # Fetch gifter ID and set in session
        cursor.execute("SELECT id FROM staff WHERE email = ?", (email,))
        gifter = cursor.fetchone()
        if gifter:
            session["gifter_id"] = gifter[0]
            return redirect("/reveal-recipient")
        else:
            return render_template(
                "confirm-phone.html",
                name=name,
                last_digits=phone[-4:],
                error="User not found in the system.",
            )
    except sqlite3.Error as e:
        return f"Database error: {e}", 500
    finally:
        conn.close()

    # Send confirmation email to the user
    send_email(
        recipient=email,
        subject="You're Registered for Secret Santa!",
        body=f"Hello {name},\n\nYou have been successfully registered for Oak Cottage Secret Santa 2024. Stay tuned for your recipient's name and details!"
    )

    conn.close()
    return redirect("/assignment")  # Redirect to the assignment page
        
####
@routes_blueprint.route("/get-recipient", methods=["GET"])
def get_recipient():
    """
    Returns the assigned recipient for the logged-in user as JSON.
    """
    try:
        # Check if the user is logged in
        gifter_id = session.get("gifter_id")
        if not gifter_id:
            logging.error("User not logged in or session expired.")
            return jsonify({"error": "User not logged in or session expired."}), 403

        # Connect to the database
        conn = sqlite3.connect("secretsanta.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Fetch the assigned recipient
        cursor.execute("""
            SELECT s.name AS recipient_name
            FROM assignments a
            JOIN staff s ON a.recipient_id = s.id
            WHERE a.gifter_id = ?
        """, (gifter_id,))
        recipient = cursor.fetchone()

        if not recipient:
            logging.warning("No recipient assigned for the user.")
            return jsonify({"error": "No recipient assigned."}), 404

        # Return the recipient's name as JSON
        return jsonify({"recipient_name": recipient["recipient_name"]})

    except sqlite3.Error as e:
        logging.error(f"Database error in get_recipient: {e}")
        return jsonify({"error": "A database error occurred."}), 500

    except Exception as e:
        logging.error(f"Unexpected error in get_recipient: {e}")
        return jsonify({"error": "An unexpected error occurred."}), 500

    finally:
        if 'conn' in locals():
            conn.close()
            
####
@routes_blueprint.route("/assign-santa")
def assign_santa():
    conn = get_db_connection()
    users = conn.execute("SELECT id, name FROM users").fetchall()

    if len(users) < 2:
        flash("At least two participants are required for Secret Santa.", "error")
        conn.close()
        return redirect(url_for("routes.index"))

    # Shuffle the users and ensure no one is assigned to themselves
    user_ids = [user["id"] for user in users]
    user_names = {user["id"]: user["name"] for user in users}
    assignments = {}

    while True:
        shuffled_ids = random.sample(user_ids, len(user_ids))
        if all(gifter != recipient for gifter, recipient in zip(user_ids, shuffled_ids)):
            assignments = dict(zip(user_ids, shuffled_ids))
            break

    # Store assignments in the database
    for gifter_id, recipient_id in assignments.items():
        conn.execute(
            "INSERT INTO assignments (gifter_id, recipient_id) VALUES (?, ?)",
            (gifter_id, recipient_id),
        )
    conn.commit()
    conn.close()

    # Flash a success message
    flash("Secret Santa assignments have been made!", "success")
    return redirect(url_for("routes.index"))

####
@routes_blueprint.route("/view-assignments")
def view_assignments():
    conn = get_db_connection()
    assignments = conn.execute(
        """
        SELECT 
            gifter.name AS gifter_name,
            gifter.email AS gifter_email,
            recipient.name AS recipient_name
        FROM assignments
        JOIN users AS gifter ON assignments.gifter_id = gifter.id
        JOIN users AS recipient ON assignments.recipient_id = recipient.id
        """
    ).fetchall()
    conn.close()

    return render_template("view_assignments.html", assignments=assignments)

####
@routes_blueprint.route("/assign-recipients", methods=["POST"])
def assign_recipients():
    try:
        # Connect to the database
        conn = sqlite3.connect("secretsanta.db")
        cursor = conn.cursor()

        # Fetch all staff IDs and names
        cursor.execute("SELECT id, name FROM staff")
        staff = cursor.fetchall()

        if len(staff) < 2:
            flash("At least two participants are required for Secret Santa.", "error")
            return redirect(url_for("routes.admin_dashboard"))

        # Shuffle staff to randomize assignments
        random.shuffle(staff)

        assignments = []
        for i in range(len(staff)):
            gifter_id = staff[i][0]  # Current staff ID
            recipient_id = staff[(i + 1) % len(staff)][0]  # Next staff ID (circular assignment)
            assignments.append((gifter_id, recipient_id))

        # Save assignments in the database
        cursor.executemany("INSERT INTO assignments (gifter_id, recipient_id) VALUES (?, ?)", assignments)
        conn.commit()

        flash("Secret Santa assignments successfully completed!", "success")
        return redirect(url_for("routes.admin_dashboard"))

    except sqlite3.Error as e:
        logging.error(f"Database error in assign_recipients: {e}")
        flash("An error occurred while assigning recipients. Please try again.", "error")
        return redirect(url_for("routes.admin_dashboard"))

    finally:
        if 'conn' in locals():
            conn.close()

####
@routes_blueprint.route("/reset-assignments")
def reset_assignments():
    conn = get_db_connection()
    conn.execute("DELETE FROM assignments")
    conn.commit()
    conn.close()

    flash("Assignments have been reset!", "success")
    return redirect(url_for("routes.index"))

####
@routes_blueprint.route("/get-names", methods=["GET"])
def get_names():
    conn = get_db_connection()
    staff = conn.execute("SELECT name FROM staff").fetchall()
    conn.close()

    # Extract names from the database rows
    names = [row["name"] for row in staff]
    return jsonify(names)

####
@routes_blueprint.route("/assign", methods=["GET"])
def assign_page():
    try:
        # Get gifter_id from session
        gifter_id = session.get("gifter_id")
        if not gifter_id:
            flash("You must confirm your details first.", "error")
            return redirect(url_for("routes.select_staff"))

        # Connect to the database
        conn = sqlite3.connect("secretsanta.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Fetch the recipient assigned to the gifter
        cursor.execute("""
            SELECT s.name AS recipient_name
            FROM assignments a
            JOIN staff s ON a.recipient_id = s.id
            WHERE a.gifter_id = ?
        """, (gifter_id,))
        recipient = cursor.fetchone()

        if not recipient:
            flash("No recipient assigned yet. Please contact the administrator.", "error")
            return redirect(url_for("routes.index"))

        recipient_name = recipient["recipient_name"]

        return render_template("assign-page.html", recipient_name=recipient_name)

    except sqlite3.Error as e:
        logging.error(f"Database error in assign_page: {e}")
        flash("An error occurred while fetching your recipient. Please try again later.", "error")
        return redirect(url_for("routes.index"))

    finally:
        if 'conn' in locals():
            conn.close()
            
####

def pre_assign_recipients():
    try:
        # Connect to the database
        conn = sqlite3.connect("secretsanta.db")
        cursor = conn.cursor()

        # Fetch all staff IDs
        cursor.execute("SELECT id FROM staff")
        staff_ids = [row[0] for row in cursor.fetchall()]

        if len(staff_ids) < 2:
            logging.error("Not enough staff members to assign recipients.")
            return "Not enough participants to assign recipients."

        # Shuffle staff IDs to randomize recipient assignments
        shuffled_ids = staff_ids[:]
        random.shuffle(shuffled_ids)

        assignments = []
        for i, gifter_id in enumerate(staff_ids):
            recipient_id = shuffled_ids[i]
            # Ensure no self-assignment
            if gifter_id == recipient_id:
                # Swap with the next person (wrap around to the start if needed)
                recipient_id = shuffled_ids[(i + 1) % len(shuffled_ids)]

            assignments.append((gifter_id, recipient_id))

        # Insert or update assignments in the database
        cursor.executemany(
            "INSERT OR REPLACE INTO assignments (gifter_id, recipient_id) VALUES (?, ?)", assignments
        )
        conn.commit()
        logging.info("Recipients assigned successfully.")
        return "Recipients assigned successfully."

    except sqlite3.Error as e:
        logging.error(f"Database error in pre_assign_recipients: {e}")
        return f"Database error: {e}"

    finally:
        if 'conn' in locals():
            conn.close()

####
@routes_blueprint.route('/admin-dashboard')
def admin_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch participants
    cursor.execute("SELECT id, name, phone, email FROM staff")
    participants = cursor.fetchall()

    # Fetch assignments
    cursor.execute("""
        SELECT s1.name as santa_name, s2.name as recipient_name
        FROM assignments
        JOIN staff s1 ON assignments.gifter_id = s1.id
        JOIN staff s2 ON assignments.recipient_id = s2.id
    """)
    assignments = cursor.fetchall()

    # Fetch unassigned participants
    cursor.execute("""
        SELECT id, name, phone, email
        FROM staff
        WHERE id NOT IN (SELECT gifter_id FROM assignments)
    """)
    unassigned_participants = cursor.fetchall()

    conn.close()
    return render_template(
        'admin-dashboard.html',
        participants=participants,
        assignments=assignments,
        unassigned_participants=unassigned_participants
    )
   

@routes_blueprint.route("/reveal-recipient")
def reveal_recipient():
    try:
        conn = sqlite3.connect("secretsanta.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        gifter_id = session.get("gifter_id")
        if not gifter_id:
            flash("You must confirm your details first.", "error")
            return redirect(url_for("routes.select_staff"))

        # Fetch the assigned recipient
        cursor.execute("""
            SELECT s.name 
            FROM assignments a
            JOIN staff s ON a.recipient_id = s.id
            WHERE a.gifter_id = ?
        """, (gifter_id,))
        recipient = cursor.fetchone()

        if not recipient:
            flash("No recipient assigned. Please contact admin.", "error")
            return redirect(url_for("routes.select_staff"))

        recipient_name = recipient["name"]
        return render_template("reveal-recipient.html", recipient_name=recipient_name)

    except Exception as e:
        logging.error(f"Error in reveal_recipient: {e}")
        flash("An error occurred while retrieving your recipient.", "error")
        return redirect(url_for("routes.select_staff"))

    finally:
        conn.close()


####
@routes_blueprint.route("/confirm-phone", methods=["GET", "POST"])
def confirm_phone():
    try:
        conn = sqlite3.connect("secretsanta.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if request.method == "POST":
            name = request.form.get("name")
            phone = request.form.get("phone")
            email = request.form.get("email")
            confirm_email = request.form.get("confirm_email")

            # Validate email match
            if email != confirm_email:
                flash("Emails do not match. Please try again.", "error")
                return redirect(url_for("routes.confirm_phone", name=name))

            # Validate phone number
            cursor.execute("SELECT id, phone FROM staff WHERE name = ?", (name,))
            staff = cursor.fetchone()

            if not staff or staff["phone"] != phone:
                flash("Phone number does not match our records.", "error")
                return redirect(url_for("routes.confirm_phone", name=name))

            # Set gifter_id in session
            session["gifter_id"] = staff["id"]

            # Redirect to reveal recipient
            return redirect(url_for("routes.reveal_recipient"))

        # For GET, display the confirmation form
        name = request.args.get("name")
        cursor.execute("SELECT phone FROM staff WHERE name = ?", (name,))
        staff = cursor.fetchone()

        if not staff:
            flash("Staff member not found. Please try again.", "error")
            return redirect(url_for("routes.select_staff"))

        # Pass last 4 digits of phone to template
        phone_last4 = staff["phone"][-4:]
        return render_template("confirm-phone.html", name=name, phone_last4=phone_last4)

    except Exception as e:
        logging.error(f"Error in confirm_phone: {e}")
        flash("An unexpected error occurred. Please try again later.", "error")
        return redirect(url_for("routes.select_staff"))

    finally:
        conn.close()
