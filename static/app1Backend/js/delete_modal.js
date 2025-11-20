// Este script maneja la lógica para el modal de confirmación de borrado.
// Se asegura de que el modal muestre la información correcta antes de eliminar un ítem.

// Espera a que todo el contenido de la página (el DOM) esté completamente cargado antes de ejecutar el código.
// Esto previene errores si el script se carga antes que los elementos HTML.
document.addEventListener('DOMContentLoaded', function () {
    
    // Busca el elemento del modal en el documento por su ID.
    const deleteModal = document.getElementById('deleteConfirmationModal');
    
    // Si el modal realmente existe en la página, procedemos a configurar su comportamiento.
    if (deleteModal) {
        
        // Añadimos un "escuchador" para el evento 'show.bs.modal'.
        // Este evento especial de Bootstrap se dispara justo cuando el modal está a punto de mostrarse.
        deleteModal.addEventListener('show.bs.modal', function (event) {
            
            // 'event.relatedTarget' es una propiedad muy útil: nos da acceso al botón exacto que abrió el modal.
            const button = event.relatedTarget;
            
            // Obtenemos el nombre del ítem a eliminar desde el atributo 'data-bs-item-name' del botón.
            // Por ejemplo: "Liceo Bicentenario" o "Juan Pérez".
            const itemName = button.getAttribute('data-bs-item-name');
            
            // Obtenemos la URL a la que se debe enviar la solicitud de eliminación desde 'data-bs-delete-url'.
            // Por ejemplo: "/instituciones/eliminar/76.123.456-7/"
            const deleteUrl = button.getAttribute('data-bs-delete-url');

            // Buscamos el lugar dentro del modal donde queremos mostrar el nombre del ítem.
            const modalBodyName = deleteModal.querySelector('.modal-body-name');
            // Actualizamos su contenido con el nombre que obtuvimos del botón.
            modalBodyName.textContent = itemName;

            // Buscamos el formulario de eliminación que está dentro del modal.
            const deleteForm = deleteModal.querySelector('#deleteForm');
            // Actualizamos el atributo 'action' del formulario con la URL de eliminación.
            // Esto asegura que cuando se presione "Sí, eliminar", la solicitud se envíe al lugar correcto.
            deleteForm.action = deleteUrl;
        });
    }
});

