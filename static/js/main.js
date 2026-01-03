/**
 * 备忘录应用 - 前端交互脚本
 */

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // 初始化工具提示
    initializeTooltips();

    // 初始化表单验证
    initializeFormValidation();

    // 初始化状态切换
    initializeStatusChanges();

    // 初始化确认对话框
    initializeConfirmations();

    // 初始化响应式导航
    initializeResponsiveNav();

    // 初始化加载状态
    initializeLoadingStates();
}

/**
 * 初始化Bootstrap工具提示
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * 初始化表单验证
 */
function initializeFormValidation() {
    const forms = document.querySelectorAll('form[data-validate="true"]');

    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                return false;
            }

            // 显示加载状态
            showLoading(this);
        });
    });
}

/**
 * 表单验证函数
 */
function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');

    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            showFieldError(field, 'This field is required');
            isValid = false;
        } else {
            clearFieldError(field);
        }
    });

    // 验证日期时间字段
    const datetimeFields = form.querySelectorAll('input[type="datetime-local"]');
    datetimeFields.forEach(field => {
        if (field.value && !isValidDateTime(field.value)) {
            showFieldError(field, 'Please enter a valid date and time');
            isValid = false;
        }
    });

    return isValid;
}

/**
 * 验证日期时间格式
 */
function isValidDateTime(dateTimeString) {
    const date = new Date(dateTimeString);
    return date instanceof Date && !isNaN(date);
}

/**
 * 显示字段错误
 */
function showFieldError(field, message) {
    clearFieldError(field);

    field.classList.add('is-invalid');

    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;

    field.parentNode.appendChild(errorDiv);
}

/**
 * 清除字段错误
 */
function clearFieldError(field) {
    field.classList.remove('is-invalid');
    const errorMsg = field.parentNode.querySelector('.invalid-feedback');
    if (errorMsg) {
        errorMsg.remove();
    }
}

/**
 * 初始化状态切换
 */
function initializeStatusChanges() {
    const statusSelects = document.querySelectorAll('select[name="new_status"]');

    statusSelects.forEach(select => {
        select.addEventListener('change', function() {
            const form = this.closest('form');
            if (form) {
                // 显示加载状态
                showLoading(form);

                // 提交表单
                form.submit();
            }
        });
    });
}

/**
 * 初始化确认对话框
 */
function initializeConfirmations() {
    const confirmButtons = document.querySelectorAll('[data-confirm]');

    confirmButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm') || 'Are you sure?';

            if (!confirm(message)) {
                e.preventDefault();
                return false;
            }
        });
    });
}

/**
 * 初始化响应式导航
 */
function initializeResponsiveNav() {
    // 移动端菜单自动关闭
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');

    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            const navbarCollapse = document.querySelector('.navbar-collapse');
            if (navbarCollapse && navbarCollapse.classList.contains('show')) {
                const bsCollapse = new bootstrap.Collapse(navbarCollapse, {
                    hide: true
                });
            }
        });
    });
}

/**
 * 初始化加载状态
 */
function initializeLoadingStates() {
    // 为所有表单添加加载状态处理
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        form.addEventListener('submit', function() {
            showLoading(this);
        });
    });
}

/**
 * 显示加载状态
 */
function showLoading(element) {
    element.classList.add('loading');

    // 禁用所有按钮
    const buttons = element.querySelectorAll('button, input[type="submit"]');
    buttons.forEach(button => {
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Loading...';
    });
}

/**
 * 隐藏加载状态
 */
function hideLoading(element) {
    element.classList.remove('loading');

    // 恢复按钮状态
    const buttons = element.querySelectorAll('button, input[type="submit"]');
    buttons.forEach(button => {
        button.disabled = false;
        // 恢复原始文本（这里需要更复杂的逻辑来保存原始文本）
        if (button.tagName === 'BUTTON') {
            button.innerHTML = button.getAttribute('data-original-text') || button.innerHTML.replace('<span class="spinner-border spinner-border-sm me-2" role="status"></span>Loading...', '');
        }
    });
}

/**
 * 显示成功消息
 */
function showSuccess(message) {
    showAlert(message, 'success');
}

/**
 * 显示错误消息
 */
function showError(message) {
    showAlert(message, 'danger');
}

/**
 * 显示警告消息
 */
function showWarning(message) {
    showAlert(message, 'warning');
}

/**
 * 显示信息消息
 */
function showInfo(message) {
    showAlert(message, 'info');
}

/**
 * 通用提示消息显示
 */
function showAlert(message, type = 'info') {
    // 移除现有的提示
    const existingAlerts = document.querySelectorAll('.alert-dismissible');
    existingAlerts.forEach(alert => alert.remove());

    // 创建新的提示
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(alertDiv);

    // 3秒后自动消失
    setTimeout(() => {
        if (alertDiv && alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 3000);
}

/**
 * 防抖函数
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * 节流函数
 */
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// 导出函数供全局使用
window.MemoApp = {
    showSuccess,
    showError,
    showWarning,
    showInfo,
    showLoading,
    hideLoading
};