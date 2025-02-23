let food = []; // Data menu yang akan diambil dari API

// Fetch data menu dari server saat halaman dimuat
async function fetchMenu() {
  try {
    const response = await fetch("/api/menu");
    const rawData = await response.json();

    console.log("Data mentah dari API:", rawData);

    if (!rawData.menu || !Array.isArray(rawData.menu)) {
      throw new TypeError(
        "Data menu yang diterima tidak valid atau bukan array."
      );
    }

    food = rawData.menu;
    generateData();
  } catch (error) {
    console.error("Error di fetchMenu:", error.message);
    alert("Gagal memuat data menu. Periksa koneksi atau server");
  }
}

// Fungsi untuk mengupdate stok
async function updateStock(name, newStock) {
  try {
    const response = await fetch("/api/update_stock", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        cart: [{ name: name, jumlah: -newStock }], // Negatif karena menambah stok
      }),
    });

    const result = await response.json();

    if (result.message === "Success") {
      alert(`Stok berhasil diperbarui!`);
      fetchMenu(); // Refresh data menu
      closeSidebar();
    } else {
      console.error("Gagal memperbarui stok:", result.error);
      alert("Gagal memperbarui stok: " + (result.error || "Unknown Error"));
    }
  } catch (error) {
    console.error("Terjadi kesalahan:", error);
    alert("Terjadi kesalahan saat memproses pembaruan stok.");
  }
}

// Generate data menu ke dalam HTML
function generateData() {
  console.log("Generate data untuk admin dimulai!", food);

  const foodList = document.getElementById("foodList");
  const stockUpdate = document.getElementById("stockUpdate");

  if (!foodList || !stockUpdate) {
    console.error("Element foodList atau stockUpdate tidak ditemukan!");
    return;
  }

  foodList.innerHTML = "";
  stockUpdate.innerHTML = "<h2>Kelola Stok</h2>"; // Reset sidebar

  food.forEach((item) => {
    console.log("Item: ${item.name}, Stock: {item.stock}");
    // Buat card makanan
    let divCard = document.createElement("div");
    divCard.classList.add("card");

    let imageData = document.createElement("img");
    imageData.setAttribute("src", item.image);
    divCard.appendChild(imageData);

    let title = document.createElement("p");
    title.innerHTML = item.name;
    divCard.appendChild(title);

    let divAction = document.createElement("div");
    divAction.classList.add("action");

    let spanData = document.createElement("span");
    spanData.innerHTML = `Stok : ${item.stock}`;
    divAction.appendChild(spanData);

    let buttonEdit = document.createElement("button");
    buttonEdit.innerHTML = "Kelola Stok";
    buttonEdit.setAttribute(
      "onclick",
      `showStockEditor("${item.name}", ${item.stock})`
    );
    divAction.appendChild(buttonEdit);

    console.log(
      "Tombol untuk ${item.name} dibuat dan memanggil showStockEditor"
    );

    divCard.appendChild(divAction);
    foodList.appendChild(divCard);
  });
}

// Tampilkan editor stok di sidebar
function showStockEditor(name, currentStock) {
  console.log(
    "Memanggil showStockEditor untuk",
    name,
    "Stock saat ini:",
    currentStock
  );

  const stockUpdate = document.getElementById("stockUpdate");
  if (!stockUpdate) {
    console.error("Element #stockUpdate tidak ditemukan di HTML!");
    return;
  }

  stockUpdate.innerHTML = `
  <div style="display: flex; justify-content: space-between; align-items: center;">
    <h2>Kelola Stock : ${name}</h2>
    <button onClick="closeSidebar()" class="close-btn">&times;</button>
    </div>
    <p>Stock saat ini : ${currentStock}</p>
    <input type="number" id="newStock" placeholder="Jumlah stock baru" />
    <button onclick="submitStock('${name}')">Update Stock</button>
  `;

  stockUpdate.style.display = "block";
}

function closeSidebar() {
  const stockUpdate = document.getElementById("stockUpdate");
  stockUpdate.style.display = "none";
  stockUpdate.innerHTML = "";
}

// Submit stok baru ke server
function submitStock(name) {
  const newStock = parseInt(document.getElementById("newStock").value);
  if (isNaN(newStock)) {
    alert("Masukkan jumlah stock yang valid!");
    return;
  }

  updateStock(name, newStock);
}

// function toRupiah(harga) {
//   var result = "";
//   harga = String(harga);
//   var arr = [];
//   var count = 0;
//   for (var i = harga.length - 1; i >= 0; i--) {
//     if (count === 3 && harga[i] != undefined) {
//       arr.push(".");
//       arr.push(harga[i]);
//       count = 1;
//     } else {
//       arr.push(harga[i]);
//       count++;
//     }
//   }
//   for (var i = arr.length - 1; i >= 0; i--) {
//     result += arr[i];
//   }
//   return result;
// }

fetchMenu();
