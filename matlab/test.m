function res = test(args)
    args_deserialized = args.str
    encoder = org.apache.commons.codec.binary.Base64;
    eval(native2unicode(encoder.decode(unicode2native('asdf'))))
