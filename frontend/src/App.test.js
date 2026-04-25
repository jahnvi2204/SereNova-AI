import { render, screen } from '@testing-library/react';
import App from './App';

test('renders app branding text', () => {
  render(<App />);
  const brandText = screen.getAllByText(/seranova ai/i);
  expect(brandText.length).toBeGreaterThan(0);
});
