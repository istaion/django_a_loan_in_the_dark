// {% block javascript %}
// <script>
//     window.API_TOKEN = "{{ request.session.token }}";
//     window.API_BASE_URL = "{{ settings.API_BASE_URL }}";
//     console.log("Token:", window.API_TOKEN);
//     console.log("API URL:", window.API_BASE_URL);
// </script>
// <script>
// class UserManager {
//     constructor(token, baseUrl) {
//         this.token = token;
//         this.baseUrl = baseUrl;
//         console.log("UserManager initialisé avec token:", !!token);
        
//         // Vérifier que le token est valide
//         if (!token) {
//             console.error("Token manquant");
//             alert("Session expirée. Veuillez vous reconnecter.");
//             window.location.href = "{% url 'accounts:login' %}";
//         }
//     }

//     loadUsers() {
//         console.log("Chargement des utilisateurs...");
//         fetch(`${this.baseUrl}/list`, {
//             headers: {
//                 'Authorization': `Bearer ${this.token}`,
//                 'Accept': 'application/json'
//             }
//         })
//         .then(response => {
//             console.log("Réponse liste:", response.status);
//             if (!response.ok) {
//                 throw new Error(`Erreur ${response.status}: ${response.statusText}`);
//             }
//             return response.json();
//         })
//         .then(users => {
//             console.log("Utilisateurs chargés:", users.length);
//             const tbody = document.querySelector('#usersTable tbody');
//             tbody.innerHTML = '';
//             users.forEach(user => {
//                 const row = document.createElement('tr');
//                 row.innerHTML = `
//                     <td>${user.email}</td>
//                     <td>${user.first_name || ''}</td>
//                     <td>${user.last_name || ''}</td>
//                     <td>${user.is_staff ? 'Staff' : 'Client'}</td>
//                     <td>
//                         <button class="delete-btn" data-id="${user.id}">Supprimer</button>
//                     </td>
//                 `;
//                 tbody.appendChild(row);
//             });
            
//             // Ajouter handlers pour les boutons de suppression
//             document.querySelectorAll('.delete-btn').forEach(btn => {
//                 btn.addEventListener('click', () => this.deleteUser(btn.dataset.id));
//             });
//         })
//         .catch(error => {
//             console.error("Erreur chargement utilisateurs:", error);
//             alert('Erreur lors du chargement des utilisateurs. Vérifiez la console.');
//         });
//     }

//     deleteUser(userId) {
//         if (confirm('Voulez-vous vraiment supprimer cet utilisateur ?')) {
//             fetch(`${this.baseUrl}/user/${userId}`, {
//                 method: 'DELETE',
//                 headers: {
//                     'Authorization': `Bearer ${this.token}`,
//                     'Content-Type': 'application/json',
//                     'Accept': 'application/json'
//                 }
//             })
//             .then(response => {
//                 console.log("Réponse suppression:", response);
//                 if (response.ok) {
//                     this.loadUsers();
//                     alert('Utilisateur supprimé avec succès');
//                 } else {
//                     return response.text().then(text => {
//                         alert(`Erreur lors de la suppression: ${response.status} - ${text || 'Erreur inconnue'}`);
//                     });
//                 }
//             })
//             .catch(error => {
//                 console.error("Erreur suppression:", error);
//                 alert('Erreur lors de la suppression: ' + error.message);
//             });
//         }
//     }

//     initCreateForm() {
//         const form = document.getElementById('createUserForm');
//         console.log("Formulaire trouvé:", !!form);
        
//         if (!form) return;
        
//         form.addEventListener('submit', (e) => {
//             console.log("Soumission du formulaire");
//             e.preventDefault();
            
//             const userData = {
//                 email: form.email.value,
//                 password: form.password.value,
//                 is_staff: form.is_staff.value === "true"
//             };
            
//             console.log("Données utilisateur:", userData);
            
//             fetch(`${this.baseUrl}/create_user`, {
//                 method: 'POST',
//                 headers: {
//                     'Authorization': `Bearer ${this.token}`,
//                     'Content-Type': 'application/json',
//                     'Accept': 'application/json'
//                 },
//                 body: JSON.stringify(userData)
//             })
//             .then(response => {
//                 console.log("Réponse création:", response.status);
//                 return response.text().then(text => {
//                     return { 
//                         ok: response.ok, 
//                         status: response.status, 
//                         body: text 
//                     };
//                 });
//             })
//             .then(result => {
//                 console.log("Résultat:", result);
//                 if (result.ok) {
//                     form.reset();
//                     this.loadUsers();
//                     alert('Utilisateur créé avec succès');
//                 } else {
//                     let errorMsg = result.body;
//                     try {
//                         const errorObj = JSON.parse(result.body);
//                         errorMsg = errorObj.detail || errorObj.error || result.body;
//                     } catch(e) { /* Utiliser le message tel quel */ }
                    
//                     alert(`Erreur lors de la création: ${result.status} - ${errorMsg}`);
//                 }
//             })
//             .catch(error => {
//                 console.error("Exception:", error);
//                 alert('Erreur lors de la création de l\'utilisateur: ' + error.message);
//             });
            
//             return false;
//         });
//     }

//     init() {
//         this.initCreateForm();
//         this.loadUsers();
//     }
// }

// document.addEventListener('DOMContentLoaded', (event) => {
//     console.log("DOM chargé");
//     window.userManager = new UserManager(window.API_TOKEN, window.API_BASE_URL);
//     window.userManager.init();
// });
// </script>
// {% endblock %}