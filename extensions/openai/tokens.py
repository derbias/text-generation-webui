def token_count(prompt):
    from modules.text_generation import encode
    tokens = encode(prompt)[0]
    return {
        'length': len(tokens)
    }


def token_encode(input):
    from modules.text_generation import encode
    tokens = encode(input)[0]
    if tokens.__class__.__name__ in ['Tensor', 'ndarray']:
        tokens = tokens.tolist()

    return {
        'tokens': tokens,
        'length': len(tokens),
    }


def token_decode(tokens):
    from modules.text_generation import decode
    output = decode(tokens)
    return {
        'text': output
    }
