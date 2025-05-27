document.addEventListener("DOMContentLoaded", () => {
    fetch("/api/stats/consumption")
        .then(res => res.json())
        .then(data => {
            new ApexCharts(document.querySelector("#ingredientConsumptionChart"), {
                chart: { type: "line" },
                series: [{ name: "Istemol", data: data.values }],
                xaxis: { categories: data.labels }
            }).render();
        });

    fetch("/api/stats/delivery")
        .then(res => res.json())
        .then(data => {
            new ApexCharts(document.querySelector("#ingredientDeliveryChart"), {
                chart: { type: "bar" },
                series: [{ name: "Yetkazilgan", data: data.values }],
                xaxis: { categories: data.labels }
            }).render();
        });

    fetch("/api/stats/monthly")
        .then(res => res.json())
        .then(data => {
            document.getElementById("preparedPortions").textContent = data.prepared;
            document.getElementById("possiblePortions").textContent = data.possible;
            document.getElementById("differencePercent").textContent = data.percent + "%";
            const alertFlag = document.getElementById("alertFlag");
            if (data.percent > 15) {
                alertFlag.innerHTML = "<span class='badge bg-danger'>❗Suiste'mol!</span>";
            }
        });
});
