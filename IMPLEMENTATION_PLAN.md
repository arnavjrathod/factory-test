## Repo Context

- **`./ui/src/App.jsx`**: This is the main component for the application UI written in React.
- **`./ui/src/styles.css`**: Contains the styling for the application, using CSS variables for colors and layout.
- **`./ui/src/main.jsx`**: Entry point which mounts the React Application.
- **`./ui/src/api.js`**: Wrapper for making API requests.
- **`./ui/index.html`**: The HTML file that contains the root div for the React app.

## Files to Change

- `ui/src/App.jsx`
- `ui/src/styles.css`
- `ui/src/main.jsx`

## Implementation Steps

1. **Add Dark Mode Styles**
   - Modify `ui/src/styles.css` to include CSS variables for dark mode, such as background, text, surface colors, etc.

2. **Implement Theme Toggle in the React App**
   - Update `ui/src/App.jsx` to include a theme switching button.
   - Add `useState` to manage the current theme state (light or dark).
   - Use `useEffect` to apply the theme based on the state by toggling a class on the body or a root div.

3. **Persist Theme Across Sessions**
   - Use localStorage to save the user's theme preference in `ui/src/App.jsx`.
   - Read the saved theme on component mount to apply it automatically.

4. **Modify Main Entry Point**
   - Potentially update `ui/src/main.jsx` to ensure any global setup is correct for theme toggling.

## Tests to Run

- Run existing tests from the `tests/` directory to ensure no current functionality is broken.
- Manually test the UI in both light and dark mode to ensure styles are applied correctly and persist across page reloads.

## Risks

- CSS changes might affect layout or introduce visual bugs if not correctly scoped.
- Potential JavaScript exceptions if localStorage is not handled properly, affecting component mounting.
- Initial page load may flash default theme before JavaScript loads and applies stored theme preferences.