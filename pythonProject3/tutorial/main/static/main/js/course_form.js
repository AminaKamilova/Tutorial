document.addEventListener('DOMContentLoaded', function() {
  // Обработка загрузки изображения
  const imageUpload = document.querySelector('#course_image');
  if (imageUpload) {
    imageUpload.addEventListener('change', function(e) {
      const file = e.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = function(event) {
          const preview = document.querySelector('.course-image-preview') ||
                         document.createElement('img');
          preview.src = event.target.result;
          preview.className = 'course-image-preview';

          const label = document.querySelector('.image-upload label');
          label.innerHTML = '';
          label.appendChild(preview);
        }
        reader.readAsDataURL(file);
      }
    });
  }
  const imageInput = document.querySelector('#id_image');
    if (imageInput) {
        imageInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(event) {

                    let preview = document.querySelector('.image-preview');
                    if (!preview) {
                        preview = document.createElement('img');
                        preview.className = 'image-preview';
                        preview.style.maxWidth = '200px';
                        preview.style.marginTop = '10px';
                        imageInput.parentNode.appendChild(preview);
                    }
                    preview.src = event.target.result;
                }
                reader.readAsDataURL(file);
            }
        });
    }
  const addLessonBtn = document.getElementById('add-lesson-btn');
  if (addLessonBtn) {
    addLessonBtn.addEventListener('click', function() {
      const container = document.getElementById('lessons-container');
      const lessonCount = container.querySelectorAll('.lesson-item').length;

      const newLesson = document.createElement('div');
      newLesson.className = 'lesson-item';
      newLesson.innerHTML = `
        <input type="hidden" name="lesson_ids" value="">
        <input type="number" name="lesson_nums" value="${lessonCount + 1}" min="1" placeholder="Номер" class="lesson-num">
        <input type="text" name="lesson_names" value="" placeholder="Название урока" required>
        <textarea name="lesson_descriptions" rows="2" placeholder="Описание урока"></textarea>
        <button type="button" class="remove-lesson-btn">×</button>
      `;

      container.appendChild(newLesson);
      setupLessonEvents(newLesson);
    });
  }

  function setupLessonEvents(lessonElement) {
    const removeBtn = lessonElement.querySelector('.remove-lesson-btn');
    if (removeBtn) {
      removeBtn.addEventListener('click', function() {
        lessonElement.remove();
        updateLessonNumbers();
      });
    }
  }

  function updateLessonNumbers() {
    const lessons = document.querySelectorAll('.lesson-item');
    lessons.forEach((lesson, index) => {
      const numInput = lesson.querySelector('.lesson-num');
      if (numInput) {
        numInput.value = index + 1;
      }
    });
  }

  document.querySelectorAll('.lesson-item').forEach(setupLessonEvents);

  const deleteBtn = document.getElementById('delete-course-btn');
  if (deleteBtn) {
    deleteBtn.addEventListener('click', function() {
      if (confirm('Вы уверены, что хотите удалить этот курс? Это действие нельзя отменить.')) {
        fetch(`/courses/delete/{{ course.course_id }}`, {
          method: 'DELETE',
          headers: {
            'X-CSRFToken': '{{ csrf_token }}',
            'Content-Type': 'application/json'
          }
        })
        .then(response => {
          if (response.ok) {
            window.location.href = '/courses/';
          } else {
            alert('Ошибка при удалении курса');
          }
        });
      }
    });
  }

  const closeBtn = document.querySelector('.close-btn');
  if (closeBtn) {
    closeBtn.addEventListener('click', function() {
      window.location.href = '{% if course %}/courses/{{ course.course_id }}{% else %}/courses/{% endif %}';
    });
  }
});