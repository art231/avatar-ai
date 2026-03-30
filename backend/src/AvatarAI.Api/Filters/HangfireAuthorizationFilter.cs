using Hangfire.Dashboard;

namespace AvatarAI.Api.Filters;

public class HangfireAuthorizationFilter : IDashboardAuthorizationFilter
{
    public bool Authorize(DashboardContext context)
    {
        var httpContext = context.GetHttpContext();
        
        // В разработке разрешаем доступ всем
        if (httpContext.RequestServices.GetRequiredService<IWebHostEnvironment>().IsDevelopment())
        {
            return true;
        }
        
        // В продакшене проверяем аутентификацию и роль администратора
        if (!httpContext.User.Identity?.IsAuthenticated ?? true)
        {
            return false;
        }
        
        // Проверяем, что пользователь имеет роль администратора
        return httpContext.User.IsInRole("Admin");
    }
}