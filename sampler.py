# samplers.py
# https://github.com/ddh0/easy-llama/

"""Submodule containing SamplerSettings class and some preset samplers"""

from typing import Optional
from sys    import maxsize

from .utils import assert_type, NoneType, print_verbose, truncate, print_warning


MAX_TEMP = float(maxsize)

class SamplerSettings:
    """
    A SamplerSettings object specifies the sampling parameters that will be
    used to control text generation. It is passed as an optional parameter to
    `Thread.__init__()`, `Model.generate()`, `Model.stream()`,
    `Model.stream_print()`, etc.
    """

    param_types: dict[str, tuple[type]] = {
        'max_len_tokens'    : (int,   NoneType),
        'top_k'             : (int,   NoneType),
        'top_p'             : (float, NoneType),
        'min_p'             : (float, NoneType),
        'temp'              : (float, NoneType),
        'frequency_penalty' : (float, NoneType),
        'presence_penalty'  : (float, NoneType),
        'repeat_penalty'    : (float, NoneType)
    }

    # NOTE: Cross-reference sampler neutralization values with
    #       llama.cpp/src/llama-sampling.cpp

    param_neutralization_values: dict[str, int | float] = {
        'max_len_tokens'    : -1,
        'top_k'             : -1,
        'top_p'             : 1.0,
        'min_p'             : 0.0,
        'temp'              : 1.0,
        'frequency_penalty' : 0.0,
        'presence_penalty'  : 0.0,
        'repeat_penalty'    : 1.0
    }

    def __init__(
        self,
        max_len_tokens    : Optional[int]   = -1,
        top_k             : Optional[int]   = -1,
        top_p             : Optional[float] = 0.95,
        min_p             : Optional[float] = 0.05,
        temp              : Optional[float] = 0.8,
        frequency_penalty : Optional[float] = 0.0,
        presence_penalty  : Optional[float] = 0.0,
        repeat_penalty    : Optional[float] = 1.0,
    ):
        """
        Construct a new SamplerSettings instance

        If a sampler parameter is unspecified, the default value from llama.cpp
        is used. If all samplers are unspecified, the behaviour is equivalent
        to `DefaultSampling`.

        If a sampler parameter is explicitly set to `None`, it will be disabled.
        When all samplers are disabled, the behaviour is equivalent to the
        preset `NoSampling` (which is the unmodified probability distribution).

        For greedy decoding, see the preset `GreedyDecoding`.
        """

        if max_len_tokens is None or max_len_tokens <= 0:
            self.max_len_tokens = \
                self.param_neutralization_values['max_len_tokens']
        else:
            self.max_len_tokens = max_len_tokens
        
        # llama_sampler_top_k_impl
        if top_k is None or top_k <= 0:
            self.top_k = self.param_neutralization_values['top_k']
        else:
            self.top_k = top_k

        # llama_sampler_top_p_apply
        if top_p is None or top_p >= 1.0:
            self.top_p = self.param_neutralization_values['top_p']
        else:
            if top_p < 0.0:
                print_warning(
                    f"top_p value of {top_p} may cause unexpected behaviour, "
                    f"typical range is between 0.0 and 1.0 inclusive"
                )
            self.top_p = top_p

        # llama_sampler_min_p_apply
        if min_p is None or min_p <= 0.0:
            self.min_p = self.param_neutralization_values['min_p']
        else:
            if min_p > 1.0:
                print_warning(
                    f"min_p value of {min_p} may cause unexpected behaviour, "
                    f"typical range is between 0.0 and 1.0 inclusive"
                )
            self.min_p = min_p

        # llama_sampler_temp_impl
        if temp is None or temp == 1.0:
            self.temp = self.param_neutralization_values['temp']
        else:
            if temp < 0.0:
                print_warning(
                    f"temp value of {temp} is equivalent to a value of 0.0"
                )
            self.temp = temp

        # llama_sampler_penalties_apply
        if frequency_penalty is None or frequency_penalty == 0.0:
            self.frequency_penalty = \
                self.param_neutralization_values['frequency_penalty']
        else:
            if frequency_penalty < 0.0:
                print_warning(
                    f"frequency_penalty value of {frequency_penalty} will "
                    f"increase repetition of tokens, use positive values to "
                    f"reduce repetition"
                )
            if (frequency_penalty > 2.0) or (frequency_penalty < -2.0):
                print_warning(
                    f"presence_penalty value of {frequency_penalty} may cause "
                    f"unexpected behaviour, typical range is -2.0 to 2.0 "
                    f"inclusive"
                )
            self.frequency_penalty = frequency_penalty

        # llama_sampler_penalties_apply
        if presence_penalty is None or presence_penalty == 0.0:
            self.presence_penalty = \
                self.param_neutralization_values['presence_penalty']
        else:
            if presence_penalty < 0.0:
                print_warning(
                    f"presence_penalty value of {presence_penalty} will "
                    f"increase repetition of tokens, use positive values to "
                    f"reduce repetition"
                )
            if (presence_penalty > 2.0) or (presence_penalty < -2.0):
                print_warning(
                    f"presence_penalty value of {presence_penalty} may cause "
                    f"unexpected behaviour, typical range is -2.0 to 2.0 "
                    f"inclusive"
                )
            self.presence_penalty = presence_penalty

        # llama_sampler_penalties_apply
        if repeat_penalty is None or repeat_penalty == 1.0:
            self.repeat_penalty = \
                self.param_neutralization_values['repeat_penalty']
        else:
            if repeat_penalty < 1.0:
                print_warning(
                    f"repeat_penalty value of {repeat_penalty} will increase "
                    f"repetition, typical range is 1.0 to 1.2 inclusive"
                )
            if repeat_penalty > 1.2:
                print_warning(
                    f"repeat_penalty value of {repeat_penalty} may reduce "
                    f"generation quality, consider using a value less than ~1.2"
                )
            self.repeat_penalty = repeat_penalty
    
    def __repr__(self) -> str:
        return \
            'SamplerSettings(' \
            f'max_len_tokens={self.max_len_tokens}, ' \
            f'top_k={self.top_k}, ' \
            f'top_p={self.top_p}, ' \
            f'min_p={self.min_p}, ' \
            f'temp={self.temp}, ' \
            f'frequency_penalty={self.frequency_penalty}, ' \
            f'presence_penalty={self.presence_penalty}, ' \
            f'repeat_penalty={self.repeat_penalty}' \
            f')'




# most likely token is always chosen
GreedyDecoding = SamplerSettings(
    top_k = 1,
    top_p = None,
    min_p = None,
    temp = 0.0
)

DefaultSampling = SamplerSettings()

# llama.cpp defaults
LlamaCPPSampling = SamplerSettings(
    top_k = 40,
    top_p = 0.9,
    min_p = 0.1,
    temp = 0.8
)
