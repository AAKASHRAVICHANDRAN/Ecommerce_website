// main.js - fetches products and renders them, simple search
async function fetchProducts(q='') {
  const url = '/api/products/' + (q ? '?search=' + encodeURIComponent(q) : '')
  const r = await fetch(url)
  return r.json()
}
function renderProducts(products){
  const container = document.getElementById('products')
  container.innerHTML = ''
  products.forEach(p=>{
    const el = document.createElement('div')
    el.className = 'card'
    el.innerHTML = `<div style="height:160px;background:#f3f4f6;display:flex;align-items:center;justify-content:center">Image</div>
      <div class="title">${p.title}</div>
      <div class="price">₹${p.price}</div>
      <a href="/product/${p.slug}/" class="view">View</a>`
    container.appendChild(el)
  })
}
document.addEventListener('DOMContentLoaded', async ()=>{
  const products = await fetchProducts()
  renderProducts(products)
  const search = document.getElementById('search')
  search.addEventListener('input', async function(){
    const q = this.value.trim()
    const ps = await fetchProducts(q)
    renderProducts(ps)
  })
  const cartCount = () => (JSON.parse(localStorage.getItem('cart')||'[]').length)
  document.getElementById('cart-count').textContent = cartCount()
})
