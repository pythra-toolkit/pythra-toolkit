# Material Design Components
Relevant source files
- [src/pythra/pythra/__pycache__/__init__.cpython-312.pyc](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__pycache__/__init__.cpython-312.pyc)
- [src/pythra/pythra/__pycache__/styles.cpython-312.pyc](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/__pycache__/styles.cpython-312.pyc)
- [src/pythra/pythra/project_template/render/js/dropdown.js](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/project_template/render/js/dropdown.js)
- [src/pythra/pythra/render_template/js/dropdown.js](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/render_template/js/dropdown.js)
- [src/pythra/pythra/styles.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/styles.py)
- [src/pythra/pythra/widgets_more.py](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets_more.py)

The PyThra Material Design library provides a set of high-level components that implement the Material 3 (M3) design system. These widgets are designed to provide a consistent look and feel, handling complex layout structures like navigation drawers, app bars, and modal sheets out of the box.

## Scaffold and App Structure

The `Scaffold` widget serves as the primary layout engine for a Material Design page. It manages the placement of major UI components and ensures they do not overlap.

### Scaffold Implementation

The `Scaffold` class [src/pythra/pythra/widgets_more.py229-245](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets_more.py#L229-L245) acts as a structural container that can host:

- **AppBar**: A top navigation bar.
- **Drawer / EndDrawer**: Side navigation panels.
- **Body**: The primary content area.
- **FloatingActionButton (FAB)**: A primary action button anchored to the bottom-right.
- **BottomNavigationBar**: A bottom-docked navigation menu.
- **BottomSheet**: A persistent or modal panel at the bottom.

### Component Relationship Diagram

This diagram illustrates how the `Scaffold` class orchestrates its children in the "Code Entity Space".

Title: Scaffold Component Orchestration

```

```

Sources: [src/pythra/pythra/widgets_more.py229-245](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets_more.py#L229-L245)[src/pythra/pythra/widgets_more.py421-440](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets_more.py#L421-L440)

## Navigation Components

### AppBar

The `AppBar`[src/pythra/pythra/widgets_more.py421-440](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets_more.py#L421-L440) provides a top-level toolbar. It typically contains a `leading` widget (like a menu icon), a `title`, and a list of `actions`.

- **Elevation**: Controlled via CSS box-shadows to simulate depth.
- **M3 Color Roles**: Defaults to `Colors.surface` or `Colors.primary` depending on the theme.

### Drawer and EndDrawer

`Drawer`[src/pythra/pythra/widgets_more.py650-670](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets_more.py#L650-L670) and `EndDrawer` are side panels that slide in from the left or right.

- **Scrim**: A semi-transparent overlay is applied to the rest of the UI when the drawer is open to block interaction with the background.
- **Modal Behavior**: Managed via the `pythra_bridge.js` which handles the CSS transitions and visibility states.

### BottomNavigationBar

The `BottomNavigationBar`[src/pythra/pythra/widgets_more.py1150-1180](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets_more.py#L1150-L1180) allows switching between primary destinations in an app. It uses `BottomNavigationBarItem` objects to define the icon and label for each destination.

Sources: [src/pythra/pythra/widgets_more.py421-440](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets_more.py#L421-L440)[src/pythra/pythra/widgets_more.py650-670](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets_more.py#L650-L670)[src/pythra/pythra/widgets_more.py1150-1180](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets_more.py#L1150-L1180)

## Feedback and Overlays

### SnackBar

The `SnackBar`[src/pythra/pythra/widgets_more.py1450-1480](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets_more.py#L1450-L1480) provides brief messages about app processes at the bottom of the screen.

- **Action**: Can include a `SnackBarAction` button.
- **Duration**: Managed by the framework to automatically dismiss after a set time.

### BottomSheet

`BottomSheet`[src/pythra/pythra/widgets_more.py1320-1350](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets_more.py#L1320-L1350) is a surface anchored to the bottom of the screen. It can be persistent (part of the scaffold) or modal (appearing over other content).

### Scrim and Elevation Data Flow

Material components use specific color roles and elevation levels defined in the `ThemeData`.

Title: Material Elevation and Scrim Data Flow

```

```

Sources: [src/pythra/pythra/styles.py188-210](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/styles.py#L188-L210)[src/pythra/pythra/widgets_more.py229-245](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets_more.py#L229-L245)

## Utility Components

### Divider

The `Divider`[src/pythra/pythra/widgets_more.py77-104](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets_more.py#L77-L104) is a thin horizontal line used to separate content.

- **Thickness**: Defaults to 1px.
- **Indent/EndIndent**: Controls the horizontal padding of the line itself [src/pythra/pythra/widgets_more.py165-166](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets_more.py#L165-L166)

### FloatingActionButton (FAB)

The `FloatingActionButton`[src/pythra/pythra/widgets_more.py980-1010](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets_more.py#L980-L1010) is a circular icon button that hovers over the content. It is typically used for the most common action on a screen.

### Placeholder

The `Placeholder` widget [src/pythra/pythra/widgets_more.py1800-1820](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets_more.py#L1800-L1820) draws a box with an "X" across it, used during development to indicate where a widget will eventually be placed.
WidgetPurposeKey Props`Divider`Visual separation`thickness`, `indent`, `color``AppBar`Top navigation/actions`title`, `leading`, `actions``FloatingActionButton`Primary screen action`icon`, `onPressed`, `backgroundColor``SnackBar`Brief feedback`content`, `action`, `duration`
Sources: [src/pythra/pythra/widgets_more.py77-104](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets_more.py#L77-L104)[src/pythra/pythra/widgets_more.py980-1010](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets_more.py#L980-L1010)[src/pythra/pythra/widgets_more.py1800-1820](https://github.com/pythra-toolkit/pythra-toolkit/blob/ec1e9028/src/pythra/pythra/widgets_more.py#L1800-L1820)