# chatbot_engine.py
# Robust text extraction + simple MISRA-aware generator with LED blink support.
# Works with Streamlit file uploader (file-like) or local PDF path.
import io
import sys

# Try optional backends
try:
    import pdfplumber
except Exception:
    pdfplumber = None

try:
    import fitz  # PyMuPDF
except Exception:
    fitz = None

MISRA_RULES = [
    "No dynamic memory allocation (malloc, free, calloc, realloc forbidden).",
    "All variables must be declared at the top of blocks.",
    "No recursion allowed.",
    "All functions must have explicit return types.",
    "Use const for read-only data.",
    "No mixed data types in expressions unless explicitly cast.",
    "Use static for internal linkage; avoid globals unless necessary.",
    "All switch statements must have a default case.",
    "Check array bounds explicitly before access.",
    "Avoid non-deterministic behavior: no undefined or unspecified constructs."
]

def extract_text(uploaded_file) -> str:
    """
    Accepts a Streamlit UploadedFile (file-like) or a filesystem path (str/Path).
    Returns extracted text. Always returns a string (possibly empty).
    Uses pdfplumber first, falls back to PyMuPDF (fitz). Catches errors and prints debug info.
    """
    text_parts = []

    # Helper: use pdfplumber from bytes buffer
    def _pdfplumber_from_bytes(b: bytes):
        nonlocal text_parts
        try:
            if pdfplumber is None:
                print("pdfplumber not installed; skipping pdfplumber extraction", file=sys.stderr)
                return False
            with pdfplumber.open(io.BytesIO(b)) as pdf:
                for i, page in enumerate(pdf.pages):
                    try:
                        ptext = page.extract_text()
                        if ptext:
                            text_parts.append(ptext)
                    except Exception as e:
                        print(f"pdfplumber: page {i} extraction error: {e}", file=sys.stderr)
            return True
        except Exception as e:
            print(f"pdfplumber open failed: {e}", file=sys.stderr)
            return False

    # Helper: use PyMuPDF (fitz) from bytes
    def _fitz_from_bytes(b: bytes):
        nonlocal text_parts
        try:
            if fitz is None:
                print("PyMuPDF (fitz) not installed; skipping fitz extraction", file=sys.stderr)
                return False
            doc = fitz.open(stream=b, filetype="pdf")
            for i, page in enumerate(doc):
                try:
                    ptext = page.get_text("text")
                    if ptext:
                        text_parts.append(ptext)
                except Exception as e:
                    print(f"fitz: page {i} extraction error: {e}", file=sys.stderr)
            doc.close()
            return True
        except Exception as e:
            print(f"fitz open failed: {e}", file=sys.stderr)
            return False

    # Handle streamlit UploadedFile (has .read) or a file path string
    try:
        if hasattr(uploaded_file, "read"):
            b = uploaded_file.read()
            # reset pointer for Streamlit (optional)
            try:
                uploaded_file.seek(0)
            except Exception:
                pass
            used = _pdfplumber_from_bytes(b)
            if not used:
                _fitz_from_bytes(b)
        else:
            # treat as path string
            path = str(uploaded_file)
            try:
                with open(path, "rb") as fh:
                    b = fh.read()
                used = _pdfplumber_from_bytes(b)
                if not used:
                    _fitz_from_bytes(b)
            except Exception as e:
                print(f"Failed to open path {path}: {e}", file=sys.stderr)
    except Exception as e:
        print(f"extract_text top-level error: {e}", file=sys.stderr)

    result = "\n".join(text_parts)
    print(f"DEBUG: extracted text length = {len(result)}", file=sys.stderr)
    return result

def ask_bot(query: str, datasheet_text: str) -> str:
    """
    Keyword-based generator. Handles 'uart', 'spi', 'gpio', 'i2c', 'timer', 'adc', 'pwm', 'blink', 'led'.
    Returns generated C code (string).
    """
    if query is None:
        query = ""
    q = query.lower()

    header_lines = [
        "/*",
        " * Auto-generated Embedded C Code (MISRA-C 2012 baseline)",
        f" * Query: {query}",
        " *",
        " * MISRA Rules Applied:"
    ]
    header_lines += [f" *  - {r}" for r in MISRA_RULES]
    header_lines.append(" */\n")
    header = "\n".join(header_lines)

    # LED blink handler (covers "blinking LED" queries)
    if ("blink" in q) or ("led" in q):
        code = r'''
#include <stdint.h>
#include <stdbool.h>

/* LED blink example - MISRA-C style
 * Replace LED_PORT/LED_PIN addresses with target MCU values from datasheet.
 */
#define LED_GPIO_MODER ((volatile uint32_t *)0x48000000U)  /* example address */
#define LED_GPIO_ODR   ((volatile uint32_t *)0x48000014U)  /* example address */

static void delay_ms(uint32_t count)
{
    /* Simple busy-wait delay. Replace with timer-based if available. */
    volatile uint32_t i;
    for (i = 0U; i < (1000U * count); ++i)
    {
        /* Prevent optimization */
        (void)i;
    }
}

void LED_Blink(uint32_t times, uint32_t on_ms, uint32_t off_ms)
{
    uint32_t idx;
    for (idx = 0U; idx < times; ++idx)
    {
        /* Set pin high (example assumes bit 0) */
        *LED_GPIO_ODR |= (uint32_t)(1U << 0);
        delay_ms(on_ms);

        /* Set pin low */
        *LED_GPIO_ODR &= (uint32_t)~(1U << 0);
        delay_ms(off_ms);
    }
}
'''
        return header + code

    # Existing peripheral templates
    if "uart" in q:
        code = r'''
#include <stdint.h>
#include <stdbool.h>

void UART_Init(void)
{
    volatile uint32_t * const UART_CR  = (uint32_t *)0x40011000U;
    volatile uint32_t * const UART_BRR = (uint32_t *)0x4001100CU;

    *UART_BRR = (uint32_t)0x1A1U;
    *UART_CR  = (uint32_t)((1U << 0) | (1U << 2) | (1U << 3));
}
'''
        return header + code

    if "spi" in q:
        code = r'''
#include <stdint.h>
#include <stdbool.h>

void SPI_Init(void)
{
    volatile uint32_t * const SPI_CR1 = (uint32_t *)0x40013000U;
    *SPI_CR1 = (uint32_t)((1U << 2) | (0x2U << 3));
    *SPI_CR1 |= (uint32_t)(1U << 6);
}
'''
        return header + code

    if "gpio" in q:
        code = r'''
#include <stdint.h>
#include <stdbool.h>

void GPIO_Init(void)
{
    volatile uint32_t * const GPIO_MODER = (uint32_t *)0x48000000U;
    *GPIO_MODER &= (uint32_t)~(0x3U << (0U * 2U));
    *GPIO_MODER |= (uint32_t)(0x1U << (0U * 2U));
}
'''
        return header + code

    if "i2c" in q:
        code = r'''
#include <stdint.h>
#include <stdbool.h>

void I2C_Init(void)
{
    volatile uint32_t * const I2C_CR1    = (uint32_t *)0x40005400U;
    volatile uint32_t * const I2C_TIMING = (uint32_t *)0x40005410U;

    *I2C_TIMING = (uint32_t)0x10420F13U;
    *I2C_CR1 |= (uint32_t)(1U << 0);
}
'''
        return header + code

    if "timer" in q:
        code = r'''
#include <stdint.h>
#include <stdbool.h>

void Timer_Init(void)
{
    volatile uint32_t * const TIM_CR1 = (uint32_t *)0x40000000U;
    volatile uint32_t * const TIM_PSC = (uint32_t *)0x40000028U;
    volatile uint32_t * const TIM_ARR = (uint32_t *)0x4000002CU;

    *TIM_PSC = (uint32_t)7999U;
    *TIM_ARR = (uint32_t)999U;
    *TIM_CR1 |= (uint32_t)(1U << 0);
}
'''
        return header + code

    if "adc" in q:
        code = r'''
#include <stdint.h>
#include <stdbool.h>

void ADC_Init(void)
{
    volatile uint32_t * const ADC_CR    = (uint32_t *)0x50000008U;
    volatile uint32_t * const ADC_CHSEL = (uint32_t *)0x50000028U;

    *ADC_CHSEL = (uint32_t)(1U << 0);
    *ADC_CR |= (uint32_t)(1U << 0);
}
'''
        return header + code

    if "pwm" in q:
        code = r'''
#include <stdint.h>
#include <stdbool.h>

void PWM_Init(void)
{
    volatile uint32_t * const TIM_CCMR1 = (uint32_t *)0x40000018U;
    volatile uint32_t * const TIM_CCER  = (uint32_t *)0x40000020U;
    volatile uint32_t * const TIM_CCR1  = (uint32_t *)0x40000034U;
    volatile uint32_t * const TIM_CR1   = (uint32_t *)0x40000000U;

    *TIM_CCMR1 |= (uint32_t)(0x6U << 4);
    *TIM_CCR1 = (uint32_t)500U;
    *TIM_CCER |= (uint32_t)(1U << 0);
    *TIM_CR1 |= (uint32_t)(1U << 0);
}
'''
        return header + code

    # default placeholder
    placeholder = r'''
/* Placeholder. No matching template found for query. */
void Device_Init(void)
{
    /* Implementation pending */
}
'''
    return header + placeholder
