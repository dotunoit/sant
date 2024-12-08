document.getElementById("assign-btn").addEventListener("click", async () => {
    const resultDiv = document.getElementById("assignment-result");
    const popUp = document.getElementById("pop-up");
    const finalResult = document.getElementById("final-result");
    const names = ["Loading Names...", "Santa's Helper", "Gifting Spirit", "Holiday Cheer"]; // Placeholder for flashing names
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

        // Show the dramatic pop-up
        finalResult.innerHTML = `
            You're the Secret Santa for <strong style="color: red;">${data.recipient_name}</strong>!
        `;
        popUp.style.display = "block";

        setTimeout(() => {
            popUp.style.display = "none";
            resultDiv.innerHTML = `
                🎁 Recipient: <strong style="color: red;">${data.recipient_name}</strong>
            `;
        }, 3000); // Show pop-up for 3 seconds
    } catch (error) {
        clearInterval(interval); // Stop flashing names
        resultDiv.textContent = "An error occurred. Please try again.";
    }
});
