document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('ingredientForm');
  const table = document.getElementById('ingredientTableBody');
  const nameInput = document.getElementById('ingredientName');
  const qtyInput = document.getElementById('ingredientQty');
  const dateInput = document.getElementById('ingredientDate');

  let data = [];

   // 🔄 Ingredientlar ro‘yxatini API orqali yuklash
  async function loadIngredients() {
    try {
      const response = await fetch("/api/ingredients/");
      if (!response.ok) throw new Error("Serverdan ma'lumot olib bo'lmadi");
      const items = await response.json();

      // ✅ To‘g‘ri nomlar bilan to‘g‘ridan-to‘g‘ri ishlatamiz
      data = items;

      console.log("✅ API'dan kelgan ma'lumot:", data);
      render();
    } catch (error) {
      console.error("Ma'lumot yuklashda xatolik:", error);
    }
  }


  // 📋 Jadvalni render qilish
  function render() {
    table.innerHTML = '';
    data.forEach((item, i) => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${i + 1}</td>
        <td>${item.name}</td>
        <td>${item.quantity}</td>
        <td>${item.delivered_at}</td>
        <td>
          <button data-id="${item.id}" class="btn btn-sm btn-danger btn-delete">🗑 O‘chirish</button>
        </td>`;
      table.appendChild(row);
    });

    document.querySelectorAll(".btn-delete").forEach(btn => {
      btn.addEventListener("click", async (e) => {
        const id = e.target.dataset.id;
        await deleteIngredient(id);
      });
    });
  }

  // ❌ Ingredientni API orqali o‘chirish
  async function deleteIngredient(id) {
    try {
      const res = await fetch(`/api/ingredients/${id}`, { method: 'DELETE' });
      if (!res.ok) throw new Error("O‘chirishda serverdan xatolik");
      data = data.filter(item => item.id != id);
      render();
    } catch (error) {
      console.error("O‘chirishda xatolik:", error);
    }
  }

  // ➕ Yangi ingredient qo‘shish
  form?.addEventListener('submit', async (e) => {
    e.preventDefault();

    const newItem = {
      name: nameInput.value.trim(),
      quantity: parseFloat(qtyInput.value),
      delivered_at: dateInput.value
    };

    if (!newItem.name || isNaN(newItem.quantity) || !newItem.delivered_at) {
      alert("❗ Iltimos, barcha maydonlarni to‘ldiring.");
      return;
    }

    try {
      const response = await fetch("/api/ingredients/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(newItem)
      });

      const addedItem = await response.json();

      if (!response.ok) {
        alert("Xatolik: " + (addedItem.detail || "Qo‘shib bo‘lmadi."));
        return;
      }

      data.push(addedItem); // ✅ Chunki API to‘g‘ri formatda qaytarayapti
      form.reset();

      const modalEl = document.getElementById('ingredientModal');
      const modal = bootstrap.Modal.getInstance(modalEl);
      modal?.hide();

      render();
    } catch (error) {
      console.error("Qo‘shishda xatolik:", error);
    }
  });

  // 🟢 Boshlanishda yuklash
  loadIngredients();
});


