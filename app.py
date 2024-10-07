from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = 'bm_capital_secret_key'

from functools import wraps

def login_required(role=None):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            if role and session.get('role') != role:
                return redirect(url_for('login'))
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

# Sample Users with roles
users = [
    {"id": 1, "username": "admin", "password": "admin123", "role": "admin"},
    {"id": 2, "username": "owner1", "password": "ownerpass", "role": "owner"},
    {"id": 3, "username": "tenant1", "password": "tenantpass", "role": "tenant"}
]
# Current logged-in user (for demo purposes)
current_user = None

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = next((u for u in users if u['username'] == username and u['password'] == password), None)

        if user:
            session['user_id'] = user['id']
            session['role'] = user['role']
            session['username'] = user['username']

            if user['role'] == 'admin':
                return redirect(url_for('admin_portal'))
            elif user['role'] == 'owner':
                return redirect(url_for('owner_portal'))
            elif user['role'] == 'tenant':
                return redirect(url_for('tenant_portal'))
        else:
            flash('Invalid username or password', 'error')

    return render_template('login.html')

# Temporary storage for tenants (will eventually use a database)
tenants = [
    {"id": 1, "name": "John Doe", "houses_rented": 2, "amount_paid": 3000},
    {"id": 2, "name": "Jane Smith", "houses_rented": 1, "amount_paid": 1500},
    {"id": 3, "name": "Mike Johnson", "houses_rented": 3, "amount_paid": 4500},

]
# Sample list of properties (You can replace this with a database later)
properties = [
    {"id": 1, "address": "123 Elm St", "houses": 3, "tenant": "John Doe"},
    {"id": 2, "address": "456 Oak Ave", "houses": 2, "tenant": "Jane Smith"},
    {"id": 3, "address": "789 Maple Rd", "houses": 1, "tenant": "Mike Johnson"}
]
# Sample data: List of houses for each property
property_houses = {
    1: [{"house_number": 1, "rented": True}, {"house_number": 2, "rented": True}, {"house_number": 3, "rented": False}],
    2: [{"house_number": 1, "rented": False}, {"house_number": 2, "rented": True}],
    3: [{"house_number": 1, "rented": True}],
}
# Home Page
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about_page():
    return render_template('about.html')

@app.route('/tenant_portal')
@login_required(role='tenant')
def tenant_portal():
    tenant = next((u for u in users if u['id'] == session['user_id']), None)
    tenant_properties = [p for p in properties if p['tenant'] == tenant['username']]  # Filter tenant's properties
    return render_template('tenant_portal.html', tenant=tenant, properties=tenant_properties)

@app.route('/admin_portal')
@login_required(role='admin')
def admin_portal():
    return render_template('admin_portal.html', tenants=tenants, properties=properties, owners=users)

@app.route('/owner_portal')
@login_required(role='owner')
def owner_portal():
    owner = next((u for u in users if u['id'] == session['user_id']), None)
    owner_properties = [p for p in properties if p['owner'] == owner['username']]
    return render_template('owner_portal.html', owner=owner, properties=owner_properties)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Route to display tenants, with search functionality
@app.route('/tenants', methods=['GET'])
def tenants_page():
    search_query = request.args.get('search')  # Get search query from URL query string
    if search_query:
        filtered_tenants = [tenant for tenant in tenants if search_query.lower() in tenant['name'].lower()]
    else:
        filtered_tenants = tenants  # Show all tenants if no search query
    
    return render_template('tenants.html', tenants=filtered_tenants)


# Route to display list of houses in a property
@app.route('/list_houses/<int:property_id>')
def list_houses(property_id):
    prop = next((p for p in properties if p['id'] == property_id), None)
    houses = property_houses.get(property_id, [])
    return render_template('list_houses.html', prop=prop, houses=houses)

# Properties page route
@app.route('/properties', methods=['GET'])
def properties_page():
    search_query = request.args.get('search')  # Get search query from URL query string
    if search_query:
        filtered_properties = [prop for prop in properties if search_query.lower() in prop['address'].lower()]
    else:
        filtered_properties = properties  # Show all properties if no search query
    
    return render_template('properties.html', properties=filtered_properties)

# Add new property route
@app.route('/add_property', methods=['POST'])
def add_property():
    address = request.form['address']
    houses = int(request.form['houses'])
    tenant = request.form['tenant']
    new_id = len(properties) + 1
    properties.append({"id": new_id, "address": address, "houses": houses, "tenant": tenant})
    flash(f'Property at "{address}" added successfully!', 'success')
    return redirect(url_for('properties_page'))

# Delete property route
@app.route('/delete_property/<int:property_id>', methods=['GET'])
def delete_property(property_id):
    prop = next((p for p in properties if p['id'] == property_id), None)
    if prop:
        properties.remove(prop)
        flash(f'Property at "{prop["address"]}" deleted successfully!', 'danger')
    return redirect(url_for('properties_page'))


# Add New Tenant Form
@app.route('/add_tenant', methods=['GET', 'POST'])
def add_tenant():
    if request.method == 'POST':
        name = request.form['name']
        houses_rented = int(request.form['houses_rented'])
        amount_paid = float(request.form['amount_paid'])
        new_id = len(tenants) + 1
        tenants.append({
            "id": new_id,
            "name": name,
            "houses_rented": houses_rented,
            "amount_paid": amount_paid
        })
        flash(f'Tenant {name} added successfully!')
        return redirect(url_for('tenants_page'))
    return render_template('add_tenant.html')

# Route to edit tenant details
@app.route('/edit_tenant/<int:tenant_id>', methods=['GET', 'POST'])
def edit_tenant(tenant_id):
    tenant = next((t for t in tenants if t["id"] == tenant_id), None)
    
    if request.method == 'POST':
        tenant['name'] = request.form['name']
        tenant['houses_rented'] = int(request.form['houses_rented'])
        tenant['amount_paid'] = float(request.form['amount_paid'])
        flash(f'Tenant "{tenant["name"]}" updated successfully!', 'success')
        return redirect(url_for('tenants_page'))

    return render_template('edit_tenant.html', tenant=tenant)

# Route to edit property details
@app.route('/edit_property/<int:property_id>', methods=['GET', 'POST'])
def edit_property(property_id):
    prop = next((p for p in properties if p['id'] == property_id), None)
    
    if request.method == 'POST':
        prop['address'] = request.form['address']
        prop['houses'] = int(request.form['houses'])
        prop['tenant'] = request.form['tenant']
        flash(f'Property at "{prop["address"]}" updated successfully!', 'success')
        return redirect(url_for('properties_page'))

    return render_template('edit_property.html', prop=prop)


# Delete Tenant
@app.route('/delete_tenant/<int:tenant_id>')
def delete_tenant(tenant_id):
    tenant = next((t for t in tenants if t["id"] == tenant_id), None)
    if tenant:
        tenants.remove(tenant)
        flash(f'Tenant {tenant["name"]} deleted successfully!')
    return redirect(url_for('tenants_page'))

# Rented Properties Page (Placeholder)
@app.route('/rented_properties/<int:tenant_id>')
def rented_properties(tenant_id):
    tenant = next((t for t in tenants if t["id"] == tenant_id), None)
    if tenant:
        # Placeholder for property information
        properties = ["House 1", "House 2"] if tenant["houses_rented"] > 1 else ["House 1"]
        return render_template('rented_properties.html', tenant=tenant, properties=properties)
    return redirect(url_for('tenants_page'))

@app.route('/payment_statement/<int:tenant_id>')
def payment_statement(tenant_id):
    tenant = next((t for t in tenants if t["id"] == tenant_id), None)
    
    if tenant:
        # Dynamically calculate payments based on the amount_paid
        # Assume a fixed installment value (e.g., 1000)
        installment = 1000
        total_paid = tenant['amount_paid']
        
        # Generate a list of payments based on installments
        payments = []
        while total_paid > 0:
            payment = min(installment, total_paid)  # Either full installment or remaining amount
            payments.append(payment)
            total_paid -= payment

        return render_template('payment_statement.html', tenant=tenant, payments=payments)
    
    # If tenant not found, redirect to the tenants page
    return redirect(url_for('tenants_page'))


if __name__ == '__main__':
    app.run(debug=True)
