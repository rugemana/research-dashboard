// Sample Data
const projects = [
    { name: "AI in Healthcare", lead: "Dr. Alice", status: "active" },
    { name: "Renewable Energy", lead: "Dr. Bob", status: "completed" },
    { name: "EdTech Solutions", lead: "Dr. Charlie", status: "active" }
];

// DOM Elements
const projectsList = document.getElementById('projects-list');
const projectForm = document.getElementById('project-form');

// Render Projects
function renderProjects() {
    projectsList.innerHTML = projects
        .map(project => `
            <li>
                <strong>${project.name}</strong><br>
                Lead: ${project.lead}<br>
                Status: <span class="status-${project.status}">${project.status}</span>
            </li>
        `)
        .join('');
}

// Initialize Chart
function initChart() {
    const ctx = document.getElementById('statusChart').getContext('2d');
    const statusCounts = {
        active: projects.filter(p => p.status === 'active').length,
        completed: projects.filter(p => p.status === 'completed').length
    };

    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Active', 'Completed'],
            datasets: [{
                data: [statusCounts.active, statusCounts.completed],
                backgroundColor: ['#3498db', '#2ecc71']
            }]
        }
    });
}

// Form Submission
projectForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const newProject = {
        name: document.getElementById('project-name').value,
        lead: document.getElementById('project-lead').value,
        status: "active"
    };
    projects.push(newProject);
    renderProjects();
    initChart(); // Refresh chart
    projectForm.reset();
});

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    renderProjects();
    initChart();
});