async function checkSeat() {
    const rollNo = document.getElementById('rollNo').value.trim();
    const errorMsg = document.getElementById('error-msg');
    
    if (!rollNo) {
        errorMsg.innerText = "Roll number enter pannunga!";
        return;
    }
    
    errorMsg.style.color = "blue";
    errorMsg.innerText = "Loading data...";
    
    try {
        const response = await fetch(`/api/get_seat?roll=${rollNo}`);
        const data = await response.json();
        
        if (data.status === "success") {
            // 1. Profile Set pandrom
            document.getElementById('s-name').innerText = data.student.name;
            document.getElementById('s-roll').innerText = data.student.roll;
            document.getElementById('s-dept').innerText = data.student.dept;
            document.getElementById('s-batch').innerText = data.student.batch;
            document.getElementById('s-gender').innerText = data.student.gender === 'M' ? 'Male' : 'Female';
            
            // 2. Table Rows Create pandrom
            const tbody = document.getElementById('exam-tbody');
            tbody.innerHTML = ""; 
            
            data.exams.forEach(exam => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${exam.exam_date}<br><small style="color:#555;">${exam.session}</small></td>
                    <td><strong>${exam.hall_number}</strong></td>
                    <td class="seat-text">${exam.seat_number}</td>
                `;
                tbody.appendChild(tr);
            });
            
            // 3. Screen Maathu
            document.getElementById('login-section').classList.add('hidden');
            document.getElementById('result-section').classList.remove('hidden');
            errorMsg.innerText = "";
        } else {
            errorMsg.style.color = "red";
            errorMsg.innerText = data.message;
        }
    } catch (error) {
        console.error("Fetch Error:", error);
        errorMsg.style.color = "red";
        errorMsg.innerText = "Server Error. Local server run aagudha nu check pannunga.";
    }
}

function goBack() {
    document.getElementById('rollNo').value = "";
    document.getElementById('result-section').classList.add('hidden');
    document.getElementById('login-section').classList.remove('hidden');
    document.getElementById('error-msg').innerText = "";
}