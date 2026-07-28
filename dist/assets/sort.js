/* 商品テーブルの並び替え(価格・特徴・メーカー)
   同じボタンを再度押すと昇順/降順を反転する。 */
(function () {
  var table = document.getElementById("product-table");
  if (!table) return;
  var tbody = table.tBodies[0];
  var buttons = document.querySelectorAll(".sort-btn");
  var current = { key: null, asc: true };

  buttons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      var key = btn.dataset.key;
      current.asc = current.key === key ? !current.asc : true;
      current.key = key;

      var rows = Array.prototype.slice.call(tbody.rows);
      rows.sort(function (a, b) {
        var va = a.dataset[key], vb = b.dataset[key];
        var cmp;
        if (key === "price") {
          cmp = Number(va) - Number(vb);
        } else {
          cmp = String(va).localeCompare(String(vb), "ja");
        }
        return current.asc ? cmp : -cmp;
      });
      rows.forEach(function (r) { tbody.appendChild(r); });

      buttons.forEach(function (b) { b.classList.remove("active", "desc"); });
      btn.classList.add("active");
      if (!current.asc) btn.classList.add("desc");
    });
  });
})();
