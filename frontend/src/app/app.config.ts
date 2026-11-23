import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { provideHttpClient } from '@angular/common/http';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { definePreset } from '@primeng/themes';
import Aura from '@primeng/themes/aura';
import { providePrimeNG } from 'primeng/config';

const FamillePreset = definePreset(Aura, {
  semantic: {
    primary: {
      50: 'color-mix(in srgb, #FF6B5B 10%, #F4EDE0)',
      100: 'color-mix(in srgb, #FF6B5B 20%, #F4EDE0)',
      200: 'color-mix(in srgb, #FF6B5B 35%, #F4EDE0)',
      300: 'color-mix(in srgb, #FF6B5B 55%, #F4EDE0)',
      400: 'color-mix(in srgb, #FF6B5B 75%, #F4EDE0)',
      500: '#FF6B5B',
      600: '#14213D',
      700: '#14213D',
      800: '#14213D',
      900: '#14213D',
      950: '#14213D',
    },
    colorScheme: {
      light: {
        surface: {
          0: '#F4EDE0',
          50: '#F4EDE0',
          100: 'color-mix(in srgb, #14213D 4%, #F4EDE0)',
          200: 'color-mix(in srgb, #14213D 12%, #F4EDE0)',
          300: 'color-mix(in srgb, #14213D 20%, #F4EDE0)',
          400: 'color-mix(in srgb, #14213D 35%, #F4EDE0)',
          500: 'color-mix(in srgb, #14213D 55%, #F4EDE0)',
          600: 'color-mix(in srgb, #14213D 70%, #F4EDE0)',
          700: '#14213D',
          800: '#14213D',
          900: '#14213D',
          950: '#14213D',
        },
        primary: {
          color: '#FF6B5B',
          contrastColor: '#14213D',
          hoverColor: '#FF6B5B',
          activeColor: '#FF6B5B',
        },
        highlight: {
          background: 'color-mix(in srgb, #FF6B5B 20%, #F4EDE0)',
          focusBackground: 'color-mix(in srgb, #FF6B5B 30%, #F4EDE0)',
          color: '#14213D',
          focusColor: '#14213D',
        },
        formField: {
          background: '{surface.0}',
          disabledBackground: '{surface.100}',
          filledBackground: '{surface.0}',
          filledHoverBackground: '{surface.0}',
          filledFocusBackground: '{surface.0}',
          borderColor: '{surface.200}',
          hoverBorderColor: '#14213D',
          focusBorderColor: '#FF6B5B',
          invalidBorderColor: '#FF6B5B',
          color: '#14213D',
          disabledColor: '{surface.500}',
          placeholderColor: '{surface.600}',
          invalidPlaceholderColor: '#14213D',
          floatLabelColor: '{surface.600}',
          floatLabelFocusColor: '#14213D',
          floatLabelActiveColor: '{surface.600}',
          floatLabelInvalidColor: '#14213D',
          iconColor: '{surface.600}',
          shadow: 'none',
        },
        text: {
          color: '#14213D',
          hoverColor: '#14213D',
          mutedColor: 'color-mix(in srgb, #14213D 70%, #F4EDE0)',
          hoverMutedColor: '#14213D',
        },
        content: {
          background: '#F4EDE0',
          hoverBackground: 'color-mix(in srgb, #14213D 5%, #F4EDE0)',
          borderColor: '{surface.200}',
          color: '#14213D',
          hoverColor: '#14213D',
        },
        overlay: {
          select: {
            background: '#F4EDE0',
            borderColor: '{surface.200}',
            color: '#14213D',
          },
          popover: {
            background: '#F4EDE0',
            borderColor: '{surface.200}',
            color: '#14213D',
          },
          modal: {
            background: '#F4EDE0',
            borderColor: '{surface.200}',
            color: '#14213D',
          },
        },
        mask: {
          background: 'rgba(20, 33, 61, 0.6)',
          color: '#F4EDE0',
        },
        list: {
          option: {
            focusBackground: 'color-mix(in srgb, #14213D 5%, #F4EDE0)',
            selectedBackground: 'color-mix(in srgb, #FF6B5B 20%, #F4EDE0)',
            selectedFocusBackground: 'color-mix(in srgb, #FF6B5B 30%, #F4EDE0)',
            color: '#14213D',
            focusColor: '#14213D',
            selectedColor: '#14213D',
            selectedFocusColor: '#14213D',
            icon: {
              color: '#14213D',
              focusColor: '#14213D',
            },
          },
        },
      },
    },
  },
  components: {
    tabs: {
      tablist: {
        background: '#F4EDE0',
        borderWidth: '0',
        borderColor: 'transparent',
      },
      tab: {
        background: 'transparent',
        hoverBackground: 'color-mix(in srgb, #14213D 5%, #F4EDE0)',
        activeBackground: '#FF6B5B',
        borderWidth: '0',
        borderColor: 'transparent',
        hoverBorderColor: 'transparent',
        activeBorderColor: 'transparent',
        color: '#14213D',
        hoverColor: '#14213D',
        activeColor: '#14213D',
        padding: '0.75rem 1rem',
        margin: '0 0.35rem 0 0',
      },
      activeBar: {
        height: '0',
      },
    },
  },
});

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideHttpClient(),
    provideAnimationsAsync(),
    providePrimeNG({
      theme: {
        preset: FamillePreset,
        options: { darkModeSelector: false },
      },
    }),
  ],
};
