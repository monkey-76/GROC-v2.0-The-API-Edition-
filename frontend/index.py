import streamlit as st
import requests

API_URL = "http://43.205.96.86:8000"

st.set_page_config(page_title="Finzaari | Exclusive Jewelry", layout="wide")

# --- 1. SESSION STATE (Memory for your JWT Token) ---
if "token" not in st.session_state:
    st.session_state["token"] = None

# --- 2. THE SELLER SIDEBAR ---
with st.sidebar:
    st.title("🛡️ Seller Admin")
    
    # If not logged in, show the login form
    if not st.session_state["token"]:
        st.markdown("### Staff Login")
        e_mail = st.text_input("Email")
        password = st.text_input("Password", type="password")
        owner_id = st.text_input("Owner ID (UUID)", help="Required by your backend header")
        
        if st.button("Login"):
            # FastAPI OAuth2 expects form data for username/password, and a Header for owner_id
            headers = {"owner-id": owner_id}
            data = {"username": e_mail, "password": password}
            
            res = requests.post(f"{API_URL}/login", data=data, headers=headers)
            if res.status_code == 200:
                st.session_state["token"] = res.json().get("access_token")
                st.rerun() # Refresh the page to show the dashboard!
            else:
                st.error("Invalid credentials")
                
    # If logged in, show the "Add Product" form
    else:
        st.success("Authenticated via JWT")
        if st.button("Logout"):
            st.session_state["token"] = None
            st.rerun()
            
        st.divider()
        st.markdown("### 📦 Add New Jewelry")
        
        with st.form("add_product_form"):
            p_name = st.text_input("Product Name")
            price = st.number_input("Price (₹)", min_value=0.0, step=500.0)
            qty = st.number_input("Quantity in Stock", min_value=1, step=1)
            caption = st.text_area("Caption / Description")
            uploaded_image = st.file_uploader("Upload Product Image", type=["png", "jpg", "jpeg"])
            
            submitted = st.form_submit_button("Upload to Finzaari")
            
            if submitted:
                if uploaded_image and p_name:
                    # Package the text data and the raw image file to send to FastAPI
                    files = {"img": (uploaded_image.name, uploaded_image.getvalue(), uploaded_image.type)}
                    data = {"p_name": p_name, "price": price, "qty": qty, "caption": caption}
                    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
                    
                    with st.spinner("Uploading to AWS S3..."):
                        post_res = requests.post(f"{API_URL}/inventory", data=data, files=files, headers=headers)
                        
                    if post_res.status_code == 200:
                        st.success("💎 Product officially listed!")
                        # Clear cache so the new product shows up immediately
                        st.cache_data.clear() 
                    else:
                        st.error(f"Upload failed: {post_res.text}")
                else:
                    st.warning("Please provide a name and an image.")

# --- 3. THE MAIN STOREFRONT (For Buyers) ---
st.title("💎 FINZAARI")
st.markdown("### Elegance in Every Piece")
st.divider()

@st.cache_data(ttl=60)
def get_inventory():
    try:
        response = requests.get(f"{API_URL}/inventory")
        if response.status_code == 200:
            return response.json()
        return []
    except Exception:
        return []

products = get_inventory()

if not products:
    st.info("No jewelry currently in stock. The vault is empty!")
else:
    cols = st.columns(3)
    for index, product in enumerate(products):
        with cols[index % 3]:
            # Extract the S3 image link from your JSON dictionary
            image_url = "https://via.placeholder.com/400?text=No+Image"
            if isinstance(product.get("img_caption"), dict) and product["img_caption"].get("img"):
                image_url = product["img_caption"]["img"]
            elif isinstance(product.get("img_caption"), str): # Fallback just in case
                image_url = product.get("img_caption")
            
            st.image(image_url, use_container_width=True)
            st.subheader(product["p_name"])
            st.write(f"**Price:** ₹{product['price']}")
            st.write(f"**In Stock:** {product['qty']}")
            
            if st.button("Buy Now", key=f"buy_{product['p_id']}", type="primary"):
                st.warning(f"Feature coming soon! (Product ID: {product['p_id']})")
