from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'bm_capital_secret_key'

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

# Home Page
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about_page():
    return render_template('about.html')

# Route to display tenants, with search functionality
@app.route('/tenants', methods=['GET'])
def tenants_page():
    search_query = request.args.get('search')  # Get search query from URL query string
    if search_query:
        filtered_tenants = [tenant for tenant in tenants if search_query.lower() in tenant['name'].lower()]
    else:
        filtered_tenants = tenants  # Show all tenants if no search query
    
    return render_template('tenants.html', tenants=filtered_tenants)


# Properties page route
@app.route('/properties', methods=['GET'])
def properties_page():
    return render_template('properties.html', properties=properties)

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
