from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'bm_capital_secret_key'

# Temporary storage for tenants (will eventually use a database)
tenants = [
    {"id": 1, "name": "John Doe", "houses_rented": 2, "amount_paid": 3000},
    {"id": 2, "name": "Jane Smith", "houses_rented": 1, "amount_paid": 1500},
]

# Home Page
@app.route('/')
def home():
    return render_template('index.html')

# Tenants Page
@app.route('/tenants')
def tenants_page():
    return render_template('tenants.html', tenants=tenants)

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
@app.route('/properties/<int:tenant_id>')
def rented_properties(tenant_id):
    tenant = next((t for t in tenants if t["id"] == tenant_id), None)
    if tenant:
        # Placeholder for property information
        properties = ["House 1", "House 2"] if tenant["houses_rented"] > 1 else ["House 1"]
        return render_template('properties.html', tenant=tenant, properties=properties)
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
