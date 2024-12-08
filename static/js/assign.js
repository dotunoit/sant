document.getElementById("assign-btn").addEventListener("click", async () => {
    const resultDiv = document.getElementById("assignment-result");
    const names = ["Loading Names..."]; // Placeholder for flashing names
    let index = 0;

    // Start flashing names
    const interval = setInterval(() => {
        resultDiv.textContent = names[index];
        index = (index + 1) % names.length;
    }, 200);

    try {
        // Fetch recipient data from the backend
        const response = await fetch("/get-recipient");
        if (!response.ok) throw new Error("Failed to fetch recipient.");
        const data = await response.json();

        clearInterval(interval); // Stop flashing names
        resultDiv.innerHTML = `
            <p style="color: red; font-size: 1.5rem; font-weight: bold;">
                Merry Christmas, <strong>${data.gifter_name}</strong>!
                You're the Secret Santa for <strong>${data.recipient_name}</strong>!
            </p>
        `;
    } catch (error) {
        clearInterval(interval); // Stop flashing names
        resultDiv.textContent = "An error occurred. Please try again.";
    }
});
