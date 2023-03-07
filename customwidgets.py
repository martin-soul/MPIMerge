

from typing import Union, Tuple, Optional,Callable

from customtkinter.windows.widgets import CTkLabel
from customtkinter.windows.widgets import CTkComboBox
from customtkinter.windows.widgets import CTkButton
from customtkinter.windows.widgets.theme import ThemeManager
from customtkinter.windows.ctk_toplevel import CTkToplevel


class CTkComboboxDialog(CTkToplevel):
    """
    Dialog with extra window, message, entry widget, confirm and ok button.
    For detailed information check out the documentation.
    """

    def __init__(self,
                 fg_color: Optional[Union[str, Tuple[str, str]]] = None,
                 text_color: Optional[Union[str, Tuple[str, str]]] = None,
                 button_fg_color: Optional[Union[str, Tuple[str, str]]] = None,
                 button_hover_color: Optional[Union[str, Tuple[str, str]]] = None,
                 button_text_color: Optional[Union[str, Tuple[str, str]]] = None,
                 entry_fg_color: Optional[Union[str, Tuple[str, str]]] = None,
                 entry_border_color: Optional[Union[str, Tuple[str, str]]] = None,
                 entry_text_color: Optional[Union[str, Tuple[str, str]]] = None,

                 title: str = "CTkDialog",
                 text: str = "CTkDialog",
                 value: list = ["option 1", "option 2"],
                 command: Union[Callable[[], None], None] = None):

        super().__init__(fg_color=fg_color)

        self._fg_color = ThemeManager.theme["CTkToplevel"]["fg_color"] if fg_color is None else self._check_color_type(fg_color)
        self._text_color = ThemeManager.theme["CTkLabel"]["text_color"] if text_color is None else self._check_color_type(button_hover_color)
        self._button_fg_color = ThemeManager.theme["CTkButton"]["fg_color"] if button_fg_color is None else self._check_color_type(button_fg_color)
        self._button_hover_color = ThemeManager.theme["CTkButton"]["hover_color"] if button_hover_color is None else self._check_color_type(button_hover_color)
        self._button_text_color = ThemeManager.theme["CTkButton"]["text_color"] if button_text_color is None else self._check_color_type(button_text_color)
        self._combo_fg_color = ThemeManager.theme["CTkEntry"]["fg_color"] if entry_fg_color is None else self._check_color_type(entry_fg_color)
        self._combo_border_color = ThemeManager.theme["CTkEntry"]["border_color"] if entry_border_color is None else self._check_color_type(entry_border_color)
        self._combo_text_color = ThemeManager.theme["CTkEntry"]["text_color"] if entry_text_color is None else self._check_color_type(entry_text_color)
        
        
        
        self._user_input: Union[str, None] = None
        self._running: bool = False
        self._text = text
        self._combo_values = value
        self._command: Callable = command
        
        self.title(title)
        self.lift()  # lift window on top
        self.attributes("-topmost", True)  # stay on top
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.after(10, self._create_widgets)  # create widgets with slight delay, to avoid white flickering of background
        self.resizable(False, False)
        self.grab_set()  # make other windows not clickable

    def _create_widgets(self):

        self.grid_columnconfigure((0, 1), weight=1)
        self.rowconfigure(0, weight=1)

        self._label = CTkLabel(master=self,
                               width=300,
                               wraplength=300,
                               fg_color="transparent",
                               text_color=self._text_color,
                               text=self._text,)
        self._label.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="ew")

        self._entry = CTkComboBox(master=self,
                               width=230,
                               fg_color=self._combo_fg_color,
                               border_color=self._combo_border_color,
                               text_color=self._combo_text_color,
                               values=self._combo_values
                               )
        self._entry.grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="ew")

        self._ok_button = CTkButton(master=self,
                                    width=100,
                                    border_width=0,
                                    fg_color=self._button_fg_color,
                                    hover_color=self._button_hover_color,
                                    text_color=self._button_text_color,
                                    text='Ok',
                                    command=self._ok_event)
        self._ok_button.grid(row=2, column=0, columnspan=2, padx=(20, 10), pady=(0, 20), sticky="nswe")

        self.after(150, lambda: self._entry.focus())  # set focus to entry with slight delay, otherwise it won't work
        self._entry.bind("<Return>", self._ok_event)

    def _ok_event(self, event=None):
        
        self.grab_release()
        self._command(self._entry.get())
        self.destroy()
        
      
        
    def _on_closing(self):
        self.grab_release()
        
        self.destroy()



    def get_input(self):
        self.master.wait_window(self)
        return self._user_input