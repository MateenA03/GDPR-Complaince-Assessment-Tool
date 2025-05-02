// This script handles the multi-step form validation and submission for the GDPR compliance report generation.
// It includes functions to validate each step, navigate between steps, and submit the form data to the server.
// It also handles the display of error messages and success messages.

// Gets references to form steps
const step1 = document.getElementById("step1");
const step2 = document.getElementById("step2");

// Function to validate the current step
function validateStep(stepElement) {
    const inputs = stepElement.querySelectorAll("input"); 
    let isValid = true;
  
    inputs.forEach((input) => { 
        const errorId = `${input.name}-error`;
        let error = document.getElementById(errorId);
        if (!input.value.trim()) { // Check if the input is empty
            isValid = false;
            input.classList.add("border-red-500");
        if (!error) { // Check if error message already exists
            error = document.createElement("p");
            error.id = errorId;
            error.textContent = "This field is required.";  // Set error message
            error.className = "text-red-500 text-sm mt-1";
            input.insertAdjacentElement("afterend", error);
        }
    } else { // If input is valid
        input.classList.remove("border-red-500"); // Remove error class if input is valid
        if (error) error.remove();
    }
    });
  
      return isValid; // Return true if all inputs are valid
}

// Function to handle the "Next" button click on the first step
function nextFromAuth() { 
    const name = document.getElementById("name");  // Get the name input field
    const email = document.getElementById("email"); // Get the email input field
  
    let valid = true; // Initialise valid to true
  
    if (!name.value.trim()) { // Check if name input is empty
        name.classList.add("border-red-500");
        valid = false; // Set valid to false
    } else { // If name input is valid
        name.classList.remove("border-red-500"); // Remove error class if input is valid
    }
  
    if (!email.value.trim() || !email.value.includes("@")) {  // Check if email input is empty or does not contain '@'
        email.classList.add("border-red-500"); 
        valid = false; // Set valid to false
    } else {
        email.classList.remove("border-red-500"); // Remove error class if input is valid
    }
  
    if (valid) { // If both inputs are valid
        document.getElementById("step0").classList.add("hidden"); // Hide the first step
        step1.classList.remove("hidden");  // Show the second step
  
        document.getElementById("progress-auth").classList.replace("bg-blue-600", "bg-gray-300"); 
        document.getElementById("progress1").classList.replace("bg-gray-300", "bg-blue-600"); 
    }
}
// Function to handle the "Next" button click on the second step
function nextStep() {  // Get the current step
    if (validateStep(step1)) {  // Validate the current step
    step1.classList.add("hidden");  // Hide the current step
    step2.classList.remove("hidden");  // Show the next step
  
    document.getElementById("progress1").classList.replace("bg-blue-600", "bg-gray-300");  
    document.getElementById("progress2").classList.replace("bg-gray-300", "bg-blue-600");
    }
}
// Function to handle the "Back" button click on the second step
function prevStep() {  // Get the current step
    step2.classList.add("hidden");  // Hide the current step
    step1.classList.remove("hidden"); // Show the previous step
  
    document.getElementById("progress2").classList.replace("bg-blue-600", "bg-gray-300");
    document.getElementById("progress1").classList.replace("bg-gray-300", "bg-blue-600");
}

document.getElementById("gdprForm").addEventListener("submit", async function (e) { // Handle form submission
    e.preventDefault();  // Prevent default form submission
  
    if (!validateStep(step2)) return;  // Validate the current step
  
    const formData = new FormData(e.target);  // Get form data
    const formJson = Object.fromEntries(formData.entries());  // Convert form data to JSON
  
    const response = await fetch("http://127.0.0.1:5000/submit", {  // Send form data to the server
        method: "POST", // Set request method to POST
        headers: { "Content-Type": "application/json" },  // Set request headers
        body: JSON.stringify(formJson),  // Convert form data to JSON string
    });
  
    if (response.ok) {  // Check if response is OK
        const blob = await response.blob();  
        const url = window.URL.createObjectURL(blob);  // Create a blob URL for the PDF file
        const a = document.createElement("a");  // Create a link element
        a.href = url;  
        a.download = "gdpr_compliance_report.pdf";  // Set the download attribute to specify the file name
        a.click();  // Programmatically click the link to trigger the download
        window.URL.revokeObjectURL(url);  // Revoke the blob URL to free up memory
  
         // ✅ Shows success message
        document.getElementById("successMessage").classList.remove("hidden");  // Show success message
        document.getElementById("successMessage").scrollIntoView({ behavior: "smooth" }); 
    } else {
        alert("Something went wrong generating the report.");  // Show error message
    }
});