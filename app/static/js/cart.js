async function addToCart(productId, quantity = 1) {
    try {
        const response = await fetch('/api/cart/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                product_id: productId,
                quantity: quantity
            })
        });

        const data = await response.json();

        if (response.ok) {
            updateCartBadge(data.cart_quantity);
            showToast('장바구니에 담았습니다');
        } else {
            showToast(data.detail || '오류가 발생했습니다', 'error');
        }
    } catch (error) {
        showToast('네트워크 오류가 발생했습니다', 'error');
    }
}

function updateCartBadge(count) {
    const badge = document.getElementById('cart-badge');
    if (badge) {
        badge.textContent = count;
        badge.style.display = count > 0 ? 'inline' : 'none';
    }
}

function showToast(message, type = 'success') {
    alert(message);
}
