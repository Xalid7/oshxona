// import { Chart } from "@/components/ui/chart"
// Global variables
let currentUser = null
let authToken = null
let products = []
let meals = []

// API Base URL
const API_BASE = "/api"

// Unit display names
const UNIT_NAMES = {
  g: "g",
  kg: "kg",
  ml: "ml",
  l: "l",
  dona: "dona",
  paket: "paket",
  quti: "quti",
}

// Initialize app
document.addEventListener("DOMContentLoaded", () => {
  initializeApp()
})

function initializeApp() {
  // Check if user is already logged in
  const token = localStorage.getItem("authToken")
  if (token) {
    authToken = token
    loadUserInfo()
  } else {
    showLogin()
  }

  // Setup event listeners
  setupEventListeners()
}

function setupEventListeners() {
  // Login form
  document.getElementById("loginFormElement").addEventListener("submit", handleLogin)

  // Logout button
  document.getElementById("logoutBtn").addEventListener("click", handleLogout)

  // Navigation
  document.querySelectorAll(".nav-link").forEach((link) => {
    link.addEventListener("click", handleNavigation)
  })

  // Modal close buttons
  document.querySelectorAll(".close").forEach((closeBtn) => {
    closeBtn.addEventListener("click", function () {
      const modal = this.closest(".modal")
      closeModal(modal.id)
    })
  })

  // Product management
  document.getElementById("addProductBtn").addEventListener("click", () => openProductModal())
  document.getElementById("productForm").addEventListener("submit", handleProductSubmit)

  // Meal management
  document.getElementById("addMealBtn").addEventListener("click", () => openMealModal())
  document.getElementById("mealForm").addEventListener("submit", handleMealSubmit)
  document.getElementById("addIngredientBtn").addEventListener("click", addIngredientForm)

  // Meal serving
  document.getElementById("serveMealForm").addEventListener("submit", handleMealServing)

  // Reports
  document.getElementById("generateReportBtn").addEventListener("click", generateMonthlyReport)

  // User management
  document.getElementById("addUserBtn").addEventListener("click", () => openModal("userModal"))
  document.getElementById("userForm").addEventListener("submit", handleUserSubmit)
}

// Authentication functions
async function handleLogin(e) {
  e.preventDefault()

  const username = document.getElementById("username").value
  const password = document.getElementById("password").value
  const errorDiv = document.getElementById("loginError")

  try {
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ username, password }),
    })

    if (response.ok) {
      const data = await response.json()
      authToken = data.access_token
      localStorage.setItem("authToken", authToken)
      await loadUserInfo()
      showDashboard()
      errorDiv.style.display = "none"
    } else {
      const error = await response.json()
      errorDiv.textContent = error.detail || "Login failed"
      errorDiv.style.display = "block"
    }
  } catch (error) {
    errorDiv.textContent = "Network error. Please try again."
    errorDiv.style.display = "block"
  }
}

async function loadUserInfo() {
  try {
    const response = await apiCall("/users/me")
    currentUser = response
    document.getElementById("currentUser").textContent =
      `${currentUser.username} (${getRoleDisplayName(currentUser.role)})`

    // Show/hide admin features
    if (currentUser.role === "admin") {
      document.getElementById("usersNavItem").style.display = "block"
    }

    return true
  } catch (error) {
    console.error("Failed to load user info:", error)
    handleLogout()
    return false
  }
}

function handleLogout() {
  authToken = null
  currentUser = null
  localStorage.removeItem("authToken")
  showLogin()
}

function showLogin() {
  document.getElementById("loginForm").style.display = "flex"
  document.getElementById("dashboard").style.display = "none"
}

function showDashboard() {
  document.getElementById("loginForm").style.display = "none"
  document.getElementById("dashboard").style.display = "grid"
  loadDashboardData()
}

// Navigation
function handleNavigation(e) {
  e.preventDefault()
  const section = e.target.getAttribute("data-section")

  // Update active nav link
  document.querySelectorAll(".nav-link").forEach((link) => link.classList.remove("active"))
  e.target.classList.add("active")

  // Show corresponding section
  document.querySelectorAll(".content-section").forEach((section) => section.classList.remove("active"))
  document.getElementById(`${section}Section`).classList.add("active")

  // Load section data
  loadSectionData(section)
}

async function loadSectionData(section) {
  switch (section) {
    case "overview":
      await loadOverviewData()
      break
    case "products":
      await loadProducts()
      break
    case "meals":
      await loadMeals()
      break
    case "servings":
      await loadServingsData()
      break
    case "reports":
      await loadReportsData()
      break
    case "users":
      if (currentUser.role === "admin") {
        await loadUsers()
      }
      break
  }
}

async function loadDashboardData() {
  await loadOverviewData()
}

// Overview functions
async function loadOverviewData() {
  try {
    const [stats, lowStockAlerts] = await Promise.all([
      apiCall("/reports/dashboard-stats"),
      apiCall("/products/low-stock/alerts"),
    ])

    // Update stats
    document.getElementById("todayServings").textContent = stats.today_servings
    document.getElementById("lowStockCount").textContent = stats.low_stock_count
    document.getElementById("totalProducts").textContent = stats.total_products
    document.getElementById("recentServings").textContent = stats.recent_servings

    // Update alerts
    displayLowStockAlerts(lowStockAlerts)
  } catch (error) {
    console.error("Failed to load overview data:", error)
  }
}

function displayLowStockAlerts(alertsData) {
  const container = document.getElementById("lowStockAlerts")

  if (alertsData.count === 0) {
    container.innerHTML =
      '<div class="alert-item alert-info"><i class="fas fa-check-circle"></i> Barcha mahsulotlar yetarli miqdorda mavjud</div>'
    return
  }

  container.innerHTML = alertsData.products
    .map(
      (product) => `
        <div class="alert-item alert-warning">
            <i class="fas fa-exclamation-triangle"></i>
            <strong>${product.name}</strong> - Qolgan: ${product.quantity} ${getUnitDisplayName(product.unit)} (Minimum: ${product.minimum_quantity} ${getUnitDisplayName(product.unit)})
        </div>
    `,
    )
    .join("")
}

// Products functions
async function loadProducts() {
  try {
    products = await apiCall("/products/")
    displayProducts()
  } catch (error) {
    console.error("Failed to load products:", error)
  }
}

function displayProducts() {
  const tbody = document.querySelector("#productsTable tbody")
  tbody.innerHTML = products
    .map(
      (product) => `
        <tr>
            <td>${product.name}</td>
            <td>${product.quantity}</td>
            <td>${getUnitDisplayName(product.unit)}</td>
            <td>${product.minimum_quantity} ${getUnitDisplayName(product.unit)}</td>
            <td>${product.delivery_date ? formatDate(product.delivery_date) : "-"}</td>
            <td>
                <span class="status-badge ${getStockStatus(product)}">
                    ${getStockStatusText(product)}
                </span>
            </td>
            <td>
                ${
                  canManageProducts()
                    ? `
                    <button class="btn btn-warning btn-sm" onclick="editProduct(${product.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-danger btn-sm" onclick="deleteProduct(${product.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                `
                    : ""
                }
            </td>
        </tr>
    `,
    )
    .join("")
}

function getStockStatus(product) {
  if (product.quantity <= product.minimum_quantity) {
    return "status-low"
  }
  return "status-normal"
}

function getStockStatusText(product) {
  if (product.quantity <= product.minimum_quantity) {
    return "Kam"
  }
  return "Normal"
}

function openProductModal(productId = null) {
  const modal = document.getElementById("productModal")
  const title = document.getElementById("productModalTitle")
  const form = document.getElementById("productForm")

  if (productId) {
    const product = products.find((p) => p.id === productId)
    title.textContent = "Mahsulotni tahrirlash"
    document.getElementById("productName").value = product.name
    document.getElementById("productQuantity").value = product.quantity
    document.getElementById("productUnit").value = product.unit
    document.getElementById("productMinimum").value = product.minimum_quantity
    document.getElementById("productDeliveryDate").value = product.delivery_date || ""
    form.dataset.productId = productId
  } else {
    title.textContent = "Mahsulot qo'shish"
    form.reset()
    delete form.dataset.productId
  }

  openModal("productModal")
}

async function handleProductSubmit(e) {
  e.preventDefault()

  const form = e.target
  const productId = form.dataset.productId
  const isEdit = !!productId

  const productData = {
    name: document.getElementById("productName").value,
    quantity: Number.parseFloat(document.getElementById("productQuantity").value),
    unit: document.getElementById("productUnit").value,
    minimum_quantity: Number.parseFloat(document.getElementById("productMinimum").value),
    delivery_date: document.getElementById("productDeliveryDate").value || null,
  }

  try {
    if (isEdit) {
      await apiCall(`/products/${productId}`, "PUT", productData)
    } else {
      await apiCall("/products/", "POST", productData)
    }

    closeModal("productModal")
    await loadProducts()
    showSuccessMessage("Mahsulot muvaffaqiyatli saqlandi")
  } catch (error) {
    showErrorMessage("Mahsulotni saqlashda xatolik yuz berdi")
  }
}

function editProduct(productId) {
  openProductModal(productId)
}

async function deleteProduct(productId) {
  if (!confirm("Mahsulotni o'chirishni tasdiqlaysizmi?")) {
    return
  }

  try {
    await apiCall(`/products/${productId}`, "DELETE")
    await loadProducts()
    showSuccessMessage("Mahsulot muvaffaqiyatli o'chirildi")
  } catch (error) {
    showErrorMessage("Mahsulotni o'chirishda xatolik yuz berdi")
  }
}

// Meals functions
async function loadMeals() {
  try {
    meals = await apiCall("/meals/")
    displayMeals()
    updateMealSelect()
  } catch (error) {
    console.error("Failed to load meals:", error)
  }
}

function displayMeals() {
  const container = document.getElementById("mealsGrid")
  container.innerHTML = meals
    .map(
      (meal) => `
        <div class="meal-card">
            <h3>${meal.name}</h3>
            <p>${meal.description || "Tavsif yo'q"}</p>
            
            <div class="meal-ingredients">
                <h4>Ingredientlar:</h4>
                ${meal.ingredients
                  .map(
                    (ing) => `
                    <div class="ingredient-item">
                        <span>${ing.product_name}</span>
                        <span>${ing.quantity}${ing.unit}</span>
                    </div>
                `,
                  )
                  .join("")}
            </div>
            
            <div class="meal-portions">
                Mumkin bo'lgan porsiyalar: ${meal.possible_portions}
            </div>
            
            <div class="meal-actions">
                ${
                  canManageMeals()
                    ? `
                    <button class="btn btn-warning btn-sm" onclick="editMeal(${meal.id})">
                        <i class="fas fa-edit"></i> Tahrirlash
                    </button>
                    <button class="btn btn-danger btn-sm" onclick="deleteMeal(${meal.id})">
                        <i class="fas fa-trash"></i> O'chirish
                    </button>
                `
                    : ""
                }
            </div>
        </div>
    `,
    )
    .join("")
}

function updateMealSelect() {
  const select = document.getElementById("mealSelect")
  select.innerHTML =
    '<option value="">Ovqat tanlang...</option>' +
    meals
      .filter((meal) => meal.possible_portions > 0)
      .map(
        (meal) => `
            <option value="${meal.id}">${meal.name} (${meal.possible_portions} porsiya)</option>
        `,
      )
      .join("")
}

function openMealModal(mealId = null) {
  const modal = document.getElementById("mealModal")
  const title = document.getElementById("mealModalTitle")
  const form = document.getElementById("mealForm")

  if (mealId) {
    const meal = meals.find((m) => m.id === mealId)
    title.textContent = "Ovqatni tahrirlash"
    document.getElementById("mealName").value = meal.name
    document.getElementById("mealDescription").value = meal.description || ""
    form.dataset.mealId = mealId

    // Load ingredients
    const container = document.getElementById("ingredientsList")
    container.innerHTML = ""
    meal.ingredients.forEach((ing) => {
      addIngredientForm(ing.product_id, ing.quantity, ing.unit)
    })
  } else {
    title.textContent = "Ovqat qo'shish"
    form.reset()
    delete form.dataset.mealId
    document.getElementById("ingredientsList").innerHTML = ""
  }

  openModal("mealModal")
}

function addIngredientForm(productId = "", quantity = "", unit = "g") {
  const container = document.getElementById("ingredientsList")
  const ingredientDiv = document.createElement("div")
  ingredientDiv.className = "ingredient-form"

  ingredientDiv.innerHTML = `
        <div class="form-group">
            <label>Mahsulot:</label>
            <select class="ingredient-product" required>
                <option value="">Mahsulot tanlang...</option>
                ${products
                  .map(
                    (p) => `
                    <option value="${p.id}" ${p.id == productId ? "selected" : ""}>${p.name} (${p.quantity}${p.unit})</option>
                `,
                  )
                  .join("")}
            </select>
        </div>
        <div class="form-group">
            <label>Miqdor:</label>
            <input type="number" class="ingredient-quantity" min="0.001" step="0.001" value="${quantity}" required>
        </div>
        <div class="form-group">
            <label>Birlik:</label>
            <select class="ingredient-unit" required>
                <option value="g" ${unit === "g" ? "selected" : ""}>Gramm (g)</option>
                <option value="kg" ${unit === "kg" ? "selected" : ""}>Kilogramm (kg)</option>
                <option value="ml" ${unit === "ml" ? "selected" : ""}>Millilitr (ml)</option>
                <option value="l" ${unit === "l" ? "selected" : ""}>Litr (l)</option>
                <option value="dona" ${unit === "dona" ? "selected" : ""}>Dona</option>
                <option value="paket" ${unit === "paket" ? "selected" : ""}>Paket</option>
                <option value="quti" ${unit === "quti" ? "selected" : ""}>Quti</option>
            </select>
        </div>
        <button type="button" class="btn btn-danger" onclick="removeIngredientForm(this)">
            <i class="fas fa-trash"></i>
        </button>
    `

  container.appendChild(ingredientDiv)
}

function removeIngredientForm(button) {
  button.closest(".ingredient-form").remove()
}

async function handleMealSubmit(e) {
  e.preventDefault()

  const form = e.target
  const mealId = form.dataset.mealId
  const isEdit = !!mealId

  // Collect ingredients
  const ingredients = []
  document.querySelectorAll(".ingredient-form").forEach((ingredientForm) => {
    const productId = Number.parseInt(ingredientForm.querySelector(".ingredient-product").value)
    const quantity = Number.parseFloat(ingredientForm.querySelector(".ingredient-quantity").value)
    const unit = ingredientForm.querySelector(".ingredient-unit").value

    if (productId && quantity && unit) {
      ingredients.push({
        product_id: productId,
        quantity: quantity,
        unit: unit,
      })
    }
  })

  if (ingredients.length === 0) {
    showErrorMessage("Kamida bitta ingredient qo'shing")
    return
  }

  const mealData = {
    name: document.getElementById("mealName").value,
    description: document.getElementById("mealDescription").value,
    ingredients: ingredients,
  }

  try {
    if (isEdit) {
      await apiCall(`/meals/${mealId}`, "PUT", mealData)
    } else {
      await apiCall("/meals/", "POST", mealData)
    }

    closeModal("mealModal")
    await loadMeals()
    showSuccessMessage("Ovqat muvaffaqiyatli saqlandi")
  } catch (error) {
    showErrorMessage("Ovqatni saqlashda xatolik yuz berdi")
  }
}

function editMeal(mealId) {
  openMealModal(mealId)
}

async function deleteMeal(mealId) {
  if (!confirm("Ovqatni o'chirishni tasdiqlaysizmi?")) {
    return
  }

  try {
    await apiCall(`/meals/${mealId}`, "DELETE")
    await loadMeals()
    showSuccessMessage("Ovqat muvaffaqiyatli o'chirildi")
  } catch (error) {
    showErrorMessage("Ovqatni o'chirishda xatolik yuz berdi")
  }
}

// Servings functions
async function loadServingsData() {
  try {
    await loadMeals() // Ensure meals are loaded for the select
    const todayServings = await apiCall("/servings/today")
    displayTodayServings(todayServings)
  } catch (error) {
    console.error("Failed to load servings data:", error)
  }
}

function displayTodayServings(servings) {
  const container = document.getElementById("todayServingsList")

  if (servings.length === 0) {
    container.innerHTML = "<p>Bugun hech qanday ovqat berilmagan</p>"
    return
  }

  container.innerHTML = servings
    .map(
      (serving) => `
        <div class="serving-item">
            <div class="serving-info">
                <h4>${serving.meal_name}</h4>
                <p>${serving.portions_served} porsiya - ${serving.username}</p>
                ${serving.notes ? `<p><em>${serving.notes}</em></p>` : ""}
            </div>
            <div class="serving-meta">
                ${formatDateTime(serving.served_at)}
            </div>
        </div>
    `,
    )
    .join("")
}

async function handleMealServing(e) {
  e.preventDefault()

  const mealId = Number.parseInt(document.getElementById("mealSelect").value)
  const portions = Number.parseInt(document.getElementById("portionsInput").value)
  const notes = document.getElementById("notesInput").value

  if (!mealId || !portions) {
    showErrorMessage("Ovqat va porsiyalar sonini tanlang")
    return
  }

  try {
    await apiCall("/servings/", "POST", {
      meal_id: mealId,
      portions_served: portions,
      notes: notes || null,
    })

    document.getElementById("serveMealForm").reset()
    await loadServingsData()
    await loadMeals() // Refresh possible portions
    showSuccessMessage("Ovqat muvaffaqiyatli berildi")
  } catch (error) {
    showErrorMessage(error.detail || "Ovqat berishda xatolik yuz berdi")
  }
}

// Reports functions
async function loadReportsData() {
  try {
    const [reports, usageData] = await Promise.all([apiCall("/reports/monthly"), apiCall("/reports/usage-analytics")])

    displayMonthlyReports(reports)
    displayUsageChart(usageData)
  } catch (error) {
    console.error("Failed to load reports data:", error)
  }
}

function displayMonthlyReports(reports) {
  const tbody = document.querySelector("#reportsTable tbody")
  tbody.innerHTML = reports
    .map(
      (report) => `
        <tr>
            <td>${report.month}/${report.year}</td>
            <td>${report.total_portions_served}</td>
            <td>${report.total_portions_possible}</td>
            <td>${report.efficiency_percentage.toFixed(1)}%</td>
            <td>
                <span class="status-badge ${report.is_suspicious ? "status-suspicious" : "status-good"}">
                    ${report.is_suspicious ? "Shubhali" : "Normal"}
                </span>
            </td>
        </tr>
    `,
    )
    .join("")
}

function displayUsageChart(usageData) {
  const ctx = document.getElementById("usageChart").getContext("2d")

  new Chart(ctx, {
    type: "bar",
    data: {
      labels: usageData.map((item) => item.product),
      datasets: [
        {
          label: "Iste'mol",
          data: usageData.map((item) => item.usage),
          backgroundColor: "rgba(102, 126, 234, 0.8)",
          borderColor: "rgba(102, 126, 234, 1)",
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
        },
      },
    },
  })
}

async function generateMonthlyReport() {
  const now = new Date()
  const year = now.getFullYear()
  const month = now.getMonth() + 1

  try {
    await apiCall(`/reports/generate-monthly/${year}/${month}`, "POST")
    await loadReportsData()
    showSuccessMessage("Oylik hisobot yaratildi")
  } catch (error) {
    showErrorMessage("Hisobot yaratishda xatolik yuz berdi")
  }
}

// Users functions
async function loadUsers() {
  try {
    const users = await apiCall("/users/")
    displayUsers(users)
  } catch (error) {
    console.error("Failed to load users:", error)
  }
}

function displayUsers(users) {
  const tbody = document.querySelector("#usersTable tbody")
  tbody.innerHTML = users
    .map(
      (user) => `
        <tr>
            <td>${user.username}</td>
            <td>${user.email}</td>
            <td>${getRoleDisplayName(user.role)}</td>
            <td>
                <span class="status-badge ${user.is_active ? "status-active" : "status-inactive"}">
                    ${user.is_active ? "Faol" : "Nofaol"}
                </span>
            </td>
            <td>${formatDateTime(user.created_at)}</td>
            <td>
                <button class="btn btn-warning btn-sm" onclick="toggleUserActive(${user.id})">
                    <i class="fas fa-toggle-${user.is_active ? "on" : "off"}"></i>
                </button>
            </td>
        </tr>
    `,
    )
    .join("")
}

async function handleUserSubmit(e) {
  e.preventDefault()

  const userData = {
    username: document.getElementById("newUsername").value,
    email: document.getElementById("newUserEmail").value,
    password: document.getElementById("newUserPassword").value,
    role: document.getElementById("newUserRole").value,
  }

  try {
    await apiCall("/users/", "POST", userData)
    closeModal("userModal")
    await loadUsers()
    showSuccessMessage("Foydalanuvchi muvaffaqiyatli yaratildi")
  } catch (error) {
    showErrorMessage("Foydalanuvchi yaratishda xatolik yuz berdi")
  }
}

async function toggleUserActive(userId) {
  try {
    await apiCall(`/users/${userId}/toggle-active`, "PUT")
    await loadUsers()
    showSuccessMessage("Foydalanuvchi holati o'zgartirildi")
  } catch (error) {
    showErrorMessage("Foydalanuvchi holatini o'zgartirishda xatolik yuz berdi")
  }
}

// Utility functions
async function apiCall(endpoint, method = "GET", data = null) {
  const config = {
    method,
    headers: {
      "Content-Type": "application/json",
    },
  }

  if (authToken) {
    config.headers.Authorization = `Bearer ${authToken}`
  }

  if (data) {
    config.body = JSON.stringify(data)
  }

  const response = await fetch(`${API_BASE}${endpoint}`, config)

  if (response.status === 401) {
    handleLogout()
    throw new Error("Unauthorized")
  }

  if (!response.ok) {
    const error = await response.json()
    throw error
  }

  return await response.json()
}

function openModal(modalId) {
  document.getElementById(modalId).style.display = "block"
}

function closeModal(modalId) {
  document.getElementById(modalId).style.display = "none"
}

function showSuccessMessage(message) {
  // You can implement a toast notification system here
  alert(message)
}

function showErrorMessage(message) {
  // You can implement a toast notification system here
  alert(message)
}

function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString("uz-UZ")
}

function formatDateTime(dateString) {
  return new Date(dateString).toLocaleString("uz-UZ")
}

function getRoleDisplayName(role) {
  const roleNames = {
    admin: "Administrator",
    manager: "Menejer",
    cook: "Oshpaz",
  }
  return roleNames[role] || role
}

function canManageProducts() {
  return currentUser && ["admin", "manager"].includes(currentUser.role)
}

function canManageMeals() {
  return currentUser && ["admin", "manager"].includes(currentUser.role)
}

function getUnitDisplayName(unit) {
  const unitNames = {
    g: "Gramm",
    kg: "Kilogramm",
    ml: "Millilitr",
    l: "Litr",
    dona: "Dona",
    paket: "Paket",
    quti: "Quti",
  }
  return unitNames[unit] || unit
}

// Close modals when clicking outside
window.onclick = (event) => {
  if (event.target.classList.contains("modal")) {
    event.target.style.display = "none"
  }
}
