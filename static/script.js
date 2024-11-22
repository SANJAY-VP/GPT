// document.addEventListener('DOMContentLoaded', function () {
//     // Auto-scroll to the bottom of the chat-box
//     const chatBox = document.querySelector('.chat-box');
//     if (chatBox) {
//         chatBox.scrollTop = chatBox.scrollHeight;
//     }

//     // Auto-scroll when a new message is added
//     const form = document.getElementById('chat-form');
//     form.addEventListener('submit', function () {
//         setTimeout(function () {
//             chatBox.scrollTop = chatBox.scrollHeight;
//         }, 100);
//     });

//     // FAQ Carousel click handling
//     const faqItems = document.querySelectorAll('.carousel-item');
//     faqItems.forEach(item => {
//         item.addEventListener('click', function () {
//             const userInputField = document.getElementById('user_input');
//             userInputField.value = this.textContent;
//         });
//     });

//     // Clone FAQ items for infinite scroll effect
//     const carousel = document.querySelector('.carousel');
//     const items = Array.from(carousel.children);
//     items.forEach(item => {
//         const clone = item.cloneNode(true);
//         carousel.appendChild(clone);
//     });
// });
